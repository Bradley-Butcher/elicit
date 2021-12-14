from prefect import task
import yaml
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import re
import itertools
import warnings

from case_extraction.case import Case, CaseField, Evidence

from case_extraction.components.qa_transformer import extract_answers
from case_extraction.components.nli_transformer import load_variables, compress

warnings.filterwarnings("ignore")


model = SentenceTransformer('all-MiniLM-L6-v2')

def similarity(answer: str, levels: List[str]):
    def _add_prefix(level: List[str]) -> str:
        return [f"this is a {l}" for l in level]
    embeddings = model.encode(_add_prefix([answer, *levels]))
    sims = [float(util.pytorch_cos_sim(embeddings[0], embeddings[i])) for i in range(1, len(embeddings))]
    return [(levels[i], s) for i, s in enumerate(sims)]

def match_similarity(answers: List[Tuple[str, float]], doc: str, levels: List[str], threshold: float) -> Union[CaseField, List[CaseField]]:
    if not answers:
        return CaseField(value=levels[-1], confidence=0.0, evidence=Evidence.no_match())
    candidates = []
    for answer, score, start, end in answers:
        output = similarity(answer, [*levels, ""])
        candidates += [(o, s * score, start, end) for o, s in output if s > threshold]
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


def filter(answers: Dict[str, Tuple[str, float]], doc:str, categories_schema: Path, threshold: float = 0.7) -> Dict[str, List[str]]:
    """
    Filter to only include answers that are above a threshold for both retrieval and category matching.
    """
    variables = load_variables(categories_schema)
    extracted_variables = {}
    for key in variables.keys():
        if variables[key] == "continuous":
            continue
        elif variables[key] == "raw":
            continue
        else:
            extracted_variables[key] = match_similarity(
                answers[key], doc=doc, levels=variables[key], threshold=threshold)
    return extracted_variables

@task
def sim_extraction(
    doc: str, 
    case: Case,
    question_schema: Path, 
    categories_schema: Path, 
    match_threshold: float = 0.3, 
    qa_threshold: float = 0.5, 
) -> Case:
    answers = extract_answers(case=case, doc=doc, question_schema=question_schema, threshold=qa_threshold)
    answer_dict = filter(answers=answers, doc=doc, categories_schema=categories_schema, threshold=match_threshold)
    case.add_dict(answer_dict)
    return case
