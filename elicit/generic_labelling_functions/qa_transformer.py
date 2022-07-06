"""Script to extract answers from a document using a Q&A Transformer model."""
from transformers import Pipeline
from pathlib import Path
from typing import Dict, List, Tuple, Union
import itertools
import warnings

from elicit.utils.loading import load_schema

warnings.filterwarnings("ignore")

model_path = Path(__file__).parent.parent.parent / "models"


def _flatten_answers(answers: Union[List[Dict], List[List[Dict]]]) -> List[Dict]:
    """
    Flatten a list of answers.

    :param answers: List of lists of answers.

    :return: Flattened list of answers.
    """
    if isinstance(answers[0], dict):
        return answers
    else:
        return list(itertools.chain.from_iterable(answers))


def _filter_candidates(answers: List[dict], threshold: float = 0.5) -> str:
    """
    Filter candidates based on their score.

    :param answers: List of candidates.
    :param threshold: Threshold for filtering.

    :return: Filtered list of candidates.
    """
    answers = _flatten_answers(answers=answers)
    return [(a["answer"], a["score"], a["start"], a["end"]) for a in answers if a["score"] > threshold]


def split_question(question: str, context: str, max_length: int = 512) -> Tuple[List[dict[str, str]], int]:
    if len(context) < max_length:
        return [{"question": question, "context": context}]
    else:
        contexts = []
        while len(context) > max_length:
            idx = max(context[:max_length].rfind(i) for i in [".", "\n"])
            if idx == -1:
                idx = max_length
            contexts.append(context[:idx])
            context = context[idx:]
        contexts.append(context)
        return [{"question": question, "context": c} for c in contexts]


def extract_answers(document_text: str, questions: List[str], qna_model: Pipeline, topk: int = 5, threshold: float = 0.3) -> Dict[str, Tuple[str, float, int, int]]:
    """
    Extract answers from a document using a Q&A Transformer model.

    :param document_text: Text Document to extract answers from.
    :param questions: List of questions to extract answers for.
    :param topk: Number of answers to return.
    :param threshold: Threshold for filtering.

    :return: Dictionary of answers.
    """
    question_input = []
    for q in questions:
        qs = split_question(question=q, context=document_text)
        question_input.extend(qs)
    print(question_input)
    res = qna_model(question_input, top_k=topk)
    return _filter_candidates(res, threshold=threshold)
