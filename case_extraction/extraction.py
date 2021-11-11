from case_extraction.qa_transformer import extract_answers
import yaml
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import re
import itertools
import warnings

warnings.filterwarnings("ignore")


schema_path = Path(__file__).parent.parent / "schema" / "categories.yml"
model = SentenceTransformer('all-MiniLM-L6-v2')
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli", device=0)


def load_variables() -> Dict[str, Union[str, List[str]]]:
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def extract_value(answers: List[Tuple[str, float]], threshold: float) -> str:
    values = [(re.findall(r'\d+', answer)[0], score)
              for answer, score in answers if score > threshold and re.findall(r'\d+', answer)]
    if not values:
        return ""
    return sorted(values, key=lambda x: x[1], reverse=True)[0][0]


def match_classify(answers: List[Tuple[str, float]], levels: List[str], threshold: float) -> str:
    if not answers:
        answers = [(levels[-1], 1.0)]
    # answers, scores = zip(*[(answer, score) for answer, score in answer])
    candidates = []
    for answer, score in answers:
        output = classifier(answer, levels, multi_label=True)
        candidates += [(output["labels"][i], output["scores"][i])
                       for i in range(len(output["labels"])) if output["scores"][i] > threshold]
        # candidates += sorted(output["labels"],
        #                      key=lambda x: output["scores"], reverse=True)[:1]
    if not candidates:
        return ""
    return sorted(candidates, key=lambda x: x[1], reverse=True)[0][0]


def extract_top(answers: List[Tuple[str, float]]) -> str:
    if not answers:
        return ""
    return sorted(answers, key=lambda x: x[1])[-1][0]


def filter(answers: Dict[str, Tuple[str, float]], threshold: float = 0.7) -> Dict[str, List[str]]:
    """
    Filter to only include answers that are above a threshold for both retrieval and category matching.
    """
    variables = load_variables()
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


def extract_variables(doc: str, match_threshold: float = 0.5, qa_threshold: float = 0.1, defendant: Optional[str] = None) -> Dict[str, List[str]]:
    answers = extract_answers(doc, threshold=qa_threshold, defendant=defendant)
    return filter(answers, threshold=match_threshold)
