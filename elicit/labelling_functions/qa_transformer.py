"""Script to extract answers from a document using a Q&A Transformer model."""
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
from pathlib import Path
from typing import Dict, List, Tuple, Union
import itertools
import warnings

from elicit.document import Document
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
        return {"question": question, "context": context}, 1
    else:
        contexts = []
        while len(context) > max_length:
            idx = max(context[:max_length].rfind(i) for i in [".", "\n"])
            if idx == -1:
                idx = max_length
            contexts.append(context[:idx])
            context = context[idx:]
        contexts.append(context)
        return [{"question": question, "context": c} for c in contexts], len(contexts)

def extract_answers(doc: str, case: Document, question_schema: Path, topk: int = 5, threshold: float = 0.3) -> Dict[str, Tuple[str, float, int, int]]:
    """
    Extract answers from a document using a Q&A Transformer model.

    :param doc: Document to extract answers from.
    :param case: Case object to substitute <masked> tokens in the question. e.g. "What crime did <defendant> commit" replaces <defendant> with case.defendant.
    :param question_schema: Path to the question schema.
    :param topk: Number of answers to return.
    :param threshold: Threshold for filtering.

    :return: Dictionary of answers.
    """
    questions = load_schema(question_schema)
    nlp = pipeline('question-answering', model="deepset/roberta-base-squad2", tokenizer="deepset/roberta-base-squad2", device=0)
    answers = {}
    question_input = []
    for k in questions.keys():
        for q in questions[k]:
            if "<" in q and ">" in q:
                sub_key = q[q.find("<")+1:q.find(">")]
                if not hasattr(case, sub_key):
                    warnings.warn(f"{sub_key} not found in Case object. Incorrectly chained. Subsituting in generic.")
                    q = q.replace("<" + sub_key + ">", sub_key)
                else:
                    q = q.replace("<" + sub_key + ">", getattr(case, sub_key).value)
            qs, splits = split_question(question=q, context=doc)
            question_input.extend(qs)
            # question_input.append({"question": q, "context": doc})
    res = nlp(question_input, top_k=topk)
    index = 0
    for k in questions.keys():
        answers[k] = _filter_candidates(
            res[index:index+(len(questions[k]) * splits)], threshold=threshold)
        index += len(questions[k]) * splits
    return answers
