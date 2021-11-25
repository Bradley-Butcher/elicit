from prefect import task
import yaml
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import re
import itertools
import warnings

from case_extraction.case import Case

from case_extraction.components.qa_transformer import extract_answers

warnings.filterwarnings("ignore")


model = SentenceTransformer('all-MiniLM-L6-v2')
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli", device=0)


def load_variables(schema_path: Path) -> Dict[str, Union[str, List[str]]]:
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def extract_value(answers: List[Tuple[str, float]], threshold: float) -> Tuple[str, float]:
    values = [(re.findall(r'\d+', answer)[0], score)
              for answer, score in answers if score > threshold and re.findall(r'\d+', answer)]
    if not values:
        return "unknown", 0.0
    values = _compress(values)
    best = max(values, key=values.get)
    return best, values[best]

def _compress(candidates: List[Tuple[str, float]]) -> Dict[str, float]:
    prob_dict = DefaultDict(float)
    prob_sum = 0.0
    for ci in candidates:
        prob_dict[ci[0]] += ci[1]
        prob_sum += ci[1]
    return {k: v / prob_sum for k, v in prob_dict.items()}

def match_classify(answers: List[Tuple[str, float]], levels: List[str], threshold: float) -> Tuple[str, float]:
    if not answers:
        return levels[-1], 0.0
    candidates = []
    for answer, score in answers:
        if answer in levels:
            candidates.append((answer, score))
        else:
            output = classifier(answer, [*levels, ""], multi_label=True)
            candidates += [(output["labels"][i], output["scores"][i] * score)
                        for i in range(len(output["labels"])) if output["scores"][i] > threshold]
    if not candidates:
        return levels[-1], 0.0
    candidates = _compress(candidates)
    best = max(candidates, key=candidates.get)
    if best == "":
        return levels[-1], 0.0
    else:
        return best, candidates[best]


def extract_top(answers: List[Tuple[str, float]]) -> Tuple[str, float]:
    if not answers:
        return ""
    return sorted(answers, key=lambda x: x[1])[-1]


def filter(answers: Dict[str, Tuple[str, float]], categories_schema: Path, threshold: float = 0.7) -> Dict[str, List[str]]:
    """
    Filter to only include answers that are above a threshold for both retrieval and category matching.
    """
    variables = load_variables(categories_schema)
    extracted_variables = {}
    for key in variables.keys():
        if variables[key] == "continuous":
            extracted_variables[key] = extract_value(
                answers[key], threshold=threshold)
        elif variables[key] == "raw":
            extracted_variables[key] = extract_top(answers[key])
        else:
            extracted_variables[key] = match_classify(
                answers[key], variables[key], threshold=threshold)
    return extracted_variables

@task
def extract_variables(
    doc: str, 
    case: Case,
    question_schema: Path, 
    categories_schema: Path, 
    use_defendants: bool = True,
    match_threshold: float = 0.5, 
    qa_threshold: float = 0.5, 
) -> Case:
    answers = extract_answers(doc, question_schema=question_schema, threshold=qa_threshold, defendant=case.defendants.value if use_defendants else None)
    answer_dict = filter(answers, categories_schema=categories_schema, threshold=match_threshold)
    case.add_dict(answer_dict)
    return case
