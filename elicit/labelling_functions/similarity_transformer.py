"""Script which uses a Sentence Similarity transformer model to assign extracted Q&A pairs to provided categories."""
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from typing import Dict, List, Tuple, Union
import warnings

from elicit.document import Document, DocumentField, Evidence

from elicit.labelling_functions.qa_transformer import extract_answers
from elicit.labelling_functions.nli_transformer import compress
from elicit.utils.loading import load_schema
from elicit.pipeline import labelling_function



warnings.filterwarnings("ignore")


model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

def similarity(answer: str, levels: List[str]):
    """
    Get the similarity score of each level to the answer.

    :param answer: The answer to compare to the levels.
    :param levels: The levels to compare to the answer.

    :return: List of (level, similarity score).
    """
    def _add_prefix(level: List[str]) -> str:
        return [f"this is a {l}" for l in level]
    embeddings = model.encode(_add_prefix([answer, *levels]), device=0)
    sims = [float(util.pytorch_cos_sim(embeddings[0], embeddings[i])) for i in range(1, len(embeddings))]
    return [(levels[i], s) for i, s in enumerate(sims)]

def match_similarity(answers: List[Tuple[str, float]], doc: str, levels: List[str], threshold: float) -> Union[DocumentField, List[DocumentField]]:
    """
    Find closest level to an answer, must pass threshold.
    
    :param answers: List of (answer, similarity score).
    :param doc: The document answers are extracted from - used to form evidence.
    :param levels: List of levels to compare to the answers.
    :param threshold: Threshold for filtering.

    :return: List of CaseFields.
    """
    if not answers:
        return DocumentField(value=levels[-1], confidence=0, evidence=Evidence.no_match())
    candidates = []
    for answer, score, start, end in answers:
        output = similarity(answer, [*levels, ""])
        candidates += [(o, s * score, start, end) for o, s in output if s > threshold]
    if not candidates:
        return DocumentField(value=levels[-1], confidence=0, evidence=Evidence.no_match())
    compressed_candidates, context = compress(candidates)
    max_candidate = max(compressed_candidates, key=compressed_candidates.get)
    output = DocumentField(
        value=max_candidate,
        confidence=compressed_candidates[max_candidate],
        evidence=Evidence.from_character_startend(doc, context[max_candidate]["start"], context[max_candidate]["end"])
    )
    if output.value == "":
        return DocumentField(value=levels[-1], confidence=0, evidence=Evidence.no_match())
    return output


def process_answers(answers: Dict[str, Tuple[str, float]], doc:str, categories_schema: Path, threshold: float = 0.7) -> Dict[str, List[str]]:
    """
    Process answers to match answers to categories.

    :param answers: Dict of answers to match to categories.
    :param doc: The document answers are extracted from - used to form evidence.
    :param categories_schema: Path to categories schema.
    :param threshold: Threshold for filtering.

    :return: Dict of variable: CaseFields.
    """
    variables = load_schema(categories_schema)
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

@labelling_function(labelling_method="Similarity Transformer", required_schemas=["question_schema", "categories_schema"])
def sim_extraction(
    doc: str, 
    document: Document,
    question_schema: Path, 
    categories_schema: Path, 
    match_threshold: float = 0.3, 
    qa_threshold: float = 0.5, 
) -> Document:
    """
    Extract variables from doc using a Sentence Similarity transformer model and a Q&A transformer model.

    Q&A transformer (doc) -> Sentence Similarity transformer (categories) -> extracted categories.

    :param doc: The document to extract variables from.
    :param case: The case to update.
    :param question_schema: Path to question schema.
    :param categories_schema: Path to categories schema.
    :param match_threshold: Threshold for filtering the similarity transformer.
    :param qa_threshold: Threshold for filtering the Q&A transformer answers.

    :return: Updated case.
    """
    answers = extract_answers(case=document, doc=doc, question_schema=question_schema, threshold=qa_threshold)
    answer_dict = process_answers(answers=answers, doc=doc, categories_schema=categories_schema, threshold=match_threshold)
    document.add_dict(answer_dict)
    return document
