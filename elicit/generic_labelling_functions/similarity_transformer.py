"""Script which uses a Sentence Similarity transformer model to assign extracted Q&A pairs to provided categories."""
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

from pathlib import Path
from typing import Dict, List, Tuple, Union
import warnings

from elicit.interface import CategoricalLabellingFunction, Extraction
from elicit.generic_labelling_functions.qa_transformer import extract_answers
from elicit.generic_labelling_functions.nli_transformer import compress


warnings.filterwarnings("ignore")


def similarity(answer: str, levels: List[str], similarity_model: SentenceTransformer):
    """
    Get the similarity score of each level to the answer.

    :param answer: The answer to compare to the levels.
    :param levels: The levels to compare to the answer.

    :return: List of (level, similarity score).
    """
    def _add_prefix(level: List[str]) -> str:
        return [f"this is a {l}" for l in level]
    embeddings = similarity_model.encode(
        _add_prefix([answer, *levels]), device=0)
    sims = [float(util.pytorch_cos_sim(embeddings[0], embeddings[i]))
            for i in range(1, len(embeddings))]
    return [(levels[i], s) for i, s in enumerate(sims)]


def match_similarity(answers: List[Tuple[str, float]], doc: str, levels: List[str], similarity_model: SentenceTransformer, filter_threshold: float, threshold: float) -> List[Extraction]:
    """
    Find closest level to an answer, must pass threshold.

    :param answers: List of (answer, similarity score).
    :param doc: The document answers are extracted from - used to form evidence.
    :param levels: List of levels to compare to the answers.
    :param threshold: Threshold for filtering.

    :return: List of CaseFields.
    """
    candidates = []
    for answer, score, start, end in answers:
        output = similarity(
            answer,
            [*levels, ""],
            similarity_model=similarity_model
        )
        candidates += [(o, s * score, start, end)
                       for o, s in output if s > filter_threshold]
    if not candidates:
        return [Extraction.abstain()]
    compressed_candidates, context = compress(candidates)

    # get all candidates that are above the threshold
    candidates = [(o, s)
                  for o, s in compressed_candidates.items() if s > threshold]

    # create a list of Extraction for each candidate
    extractions = []
    for candidate, score in candidates:
        if candidate == "":
            continue
        extractions.append(Extraction.from_character_startend(
            doc,
            candidate,
            score,
            context[candidate]["start"],
            context[candidate]["end"]
        ))

    if len(extractions) == 0:
        return [Extraction.abstain()]
    else:
        return extractions


class SimilarityLabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)
        self.filter_threshold = 0.5
        self.qna_threshold = 0.3

    def load(self) -> None:
        self.similarity_model = SentenceTransformer(
            'all-MiniLM-L6-v2', device='cuda')
        self.qna_model = pipeline(
            'question-answering',
            model="deepset/roberta-base-squad2",
            tokenizer="deepset/roberta-base-squad2", device=0
        )

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)
        final_threshold = 1 / (len(categories) + 1)
        answers = extract_answers(
            document_text,
            questions=questions,
            qna_model=self.qna_model,
            threshold=self.qna_threshold
        )
        extractions = match_similarity(
            answers,
            doc=document_text,
            levels=categories,
            similarity_model=self.similarity_model,
            filter_threshold=self.filter_threshold,
            threshold=final_threshold
        )
        self.push_many(document_name, variable_name, extractions)

    def train(self, document_name: str, variable_name: str, extraction: Extraction):
        pass

    @property
    def labelling_method(self) -> str:
        return "Q&A → Similarity Transformer"
