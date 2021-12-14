from prefect import task
import yaml
from transformers import pipeline
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import re
import itertools
import warnings

from case_extraction.case import Case, CaseField, Evidence

from case_extraction.components.qa_transformer import extract_answers

warnings.filterwarnings("ignore")

classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli", device=0)


def load_variables(schema_path: Path) -> Dict[str, Union[str, List[str]]]:
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def extract_value(answers: List[Tuple[str, float, int, int]], doc: str, threshold: float) -> Union[CaseField, List[CaseField]]:
    values = [(re.findall(r'\d+', answer)[0], score, start, end)
              for answer, score, start, end in answers if score > threshold and re.findall(r'\d+', answer)]
    if not values:
        return "unknown", 0.0
    values, context = compress(values)
    output = [CaseField(value=k, confidence=v, evidence=Evidence.from_character_startend(doc, context[k]["start"], context[k]["end"])) for k, v in values.items()]
    if len(output) == 1:
        return output[0]
    return output


def compress(candidates: List[Tuple[str, float, int, int]]) -> Dict[str, float]:
    prob_dict = DefaultDict(float)
    prob_sum = 0.0
    max_context = {}
    max_candidate = DefaultDict(float)
    for candidate, prob, start, end in candidates:
        if prob > max_candidate[candidate]:
            max_candidate[candidate] = prob
            max_context[candidate] = {"start": start, "end": end}
    for ci in candidates:
        prob_dict[ci[0]] += ci[1]
        prob_sum += ci[1]
    return {k: v / prob_sum for k, v in prob_dict.items()}, max_context

def match_classify(answers: List[Tuple[str, float]], doc: str, levels: List[str], threshold: float) -> Tuple[str, float]:
    """
    Match answers from the Q&A Transformer to the levels of the variable.
    """
    if not answers:
        return CaseField(value=levels[-1], confidence=0.0, evidence=Evidence.no_match())
    candidates = []
    for answer, score, start, end in answers:
        if answer in levels:
            candidates.append((answer, score, start, end))
        else:
            output = classifier(answer, [*levels, ""], multi_label=True)
            candidates += [(output["labels"][i], output["scores"][i] * score, start, end)
                        for i in range(len(output["labels"])) if output["scores"][i] > threshold]
    if not candidates:
        return CaseField(value=levels[-1], confidence=0.0, evidence=Evidence.no_match())
    compressed_candidates, context = compress(candidates)
    max_candidate = max(compressed_candidates, key=compressed_candidates.get)
    output = CaseField(
        value=max_candidate,
        confidence=compressed_candidates[max_candidate],
        evidence=Evidence.from_character_startend(doc, context[max_candidate]["start"], context[max_candidate]["end"])
    )
    if output.value == "":
        return CaseField(value=levels[-1], confidence=0.0, evidence=Evidence.no_match())
    return output


def extract_top(answers: List[Tuple[str, float, int, int]], doc: str) -> List[CaseField]:
    if not answers:
        return CaseField(value="unknown", confidence=0.0, evidence=Evidence.no_match())
    answers, context = compress(answers)
    return [CaseField(value=k, confidence=v, evidence=Evidence.from_character_startend(doc, context[k]["start"], context[k]["end"])) for k, v in answers.items()]


def filter(answers: Dict[str, Tuple[str, float, int, int]], doc: str, categories_schema: Path, threshold: float = 0.7) -> Dict[str, List[str]]:
    """
    Filter to only include answers that are above a threshold for both retrieval and category matching.
    """
    variables = load_variables(categories_schema)
    extracted_variables = {}
    for key in variables.keys():
        if variables[key] == "continuous":
            extracted_variables[key] = extract_value(
                answers=answers[key], doc=doc, threshold=threshold)
        elif variables[key] == "raw":
            extracted_variables[key] = extract_top(answers=answers[key], doc=doc)
        else:
            extracted_variables[key] = match_classify(answers=answers[key], doc=doc, levels=variables[key], threshold=threshold)
    return extracted_variables

@task
def nli_extraction(
    doc: str, 
    case: Case,
    question_schema: Path, 
    categories_schema: Path, 
    match_threshold: float = 0.3, 
    qa_threshold: float = 0.5, 
) -> Case:
    answers = extract_answers(doc=doc, case=case, question_schema=question_schema, threshold=qa_threshold)
    answer_dict = filter(answers, doc=doc, categories_schema=categories_schema, threshold=match_threshold)
    case.add_dict(answer_dict)
    return case
