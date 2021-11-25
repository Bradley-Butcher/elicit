import yaml
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import itertools
import warnings

warnings.filterwarnings("ignore")

model_path = Path(__file__).parent.parent.parent / "models"
model = AutoModelForQuestionAnswering.from_pretrained(
    str(model_path.resolve()))
tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")

def load_questions(schema_path: Path) -> Dict[str, List[str]]:
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)


def _flatten_answers(answers: Union[List[Dict], List[List[Dict]]]) -> List[Dict]:
    if isinstance(answers[0], dict):
        return answers
    else:
        return list(itertools.chain.from_iterable(answers))


def _filter_candidates(answers: List[dict], threshold: float = 0.5) -> str:
    answers = _flatten_answers(answers=answers)
    return [(a["answer"], a["score"]) for a in answers if a["score"] > threshold]


def _subsitute_defendant(question: str, defendant: str):
    question = question.replace("offender", defendant)
    return question


def extract_answers(doc: str, question_schema: Path, topk: int = 5, threshold: float = 0.3, defendant: Optional[str] = None) -> Dict[str, Tuple[str, float]]:
    questions = load_questions(question_schema)
    nlp = pipeline('question-answering',
                   model=model, tokenizer=tokenizer, device=0)
    answers = {}
    question_input = []
    for k in questions.keys():
        for q in questions[k]:
            if defendant:
                if k == "defendants":
                    answers[k] = [(defendant, 1.0)]
                    continue
                else:
                    q = _subsitute_defendant(question=q, defendant=defendant)
            question_input.append({"question": q, "context": doc})
    res = nlp(question_input, top_k=topk)
    index = 0
    for k in questions.keys():
        if defendant and k == "defendants":
            continue
        answers[k] = _filter_candidates(
            res[index:index+len(questions[k])], threshold=threshold)
        index += len(questions[k])
    return answers
