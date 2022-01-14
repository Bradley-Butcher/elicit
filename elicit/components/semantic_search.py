"""Script to extract answers from a document using a Sentence Similarity Transformer model trained on Q&A pairs."""
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from prefect import task
import yaml

from elicit.case import Case, CaseField, Evidence
from elicit.utils.loading import load_schema

model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

def sentence_similarities(queries: list[str], sentences: list[str], k: int = 5) -> dict[str, float]:
    """
    Get the similarity score of each sentence in the document to each query.

    :param queries: The queries to compare to the document.
    :param sentences: The sentences to compare to the queries.
    :param k: The number of sentences to return.

    :return: Dictionary of sentence: score.
    """
    #Encode query and documents
    sentence_scores = {}
    for query in queries:
        query_emb = model.encode(query)
        doc_emb = model.encode(sentences)

        #Compute dot score between query and all document embeddings
        scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()

        #Combine docs & scores
        doc_score_pairs = list(zip(sentences, scores))

        for sentence, score in doc_score_pairs:
            if sentence in sentence_scores:
                sentence_scores[sentence] += score
            else:
                sentence_scores[sentence] = score
    for sentence in sentence_scores:
        sentence_scores[sentence] /= len(queries)
    return dict(sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:k])

def doc_similarities(queries: list[str], doc: str) -> dict[str, float]:
    """
    :param query: The query to compare to the document.
    :param doc: The document to compare to the query.

    Returns the most similar sentence and its similarity score.
    """
    sentences = doc.split(".") # should find a better way to split sentences - this is very basic
    return sentence_similarities(queries, sentences)


def match_levels(sentence_score: dict[str, float], levels: list[str], threshold: float) -> tuple[str, str, float]:
    """
    Find closest level to a sentence, must pass threshold.

    :param sentence_score: Dictionary of sentence: score.
    :param levels: List of levels to search for.
    :param threshold: Threshold for filtering.

    :return: Tuple of level, sentence, score.
    """
    max_sentence = None
    max_score = -1
    max_level = None
    for sentence, score in sentence_score.items():
        level, level_score = sentence_similarities([sentence], levels, k=1).popitem()
        if level_score * score > max_score and level_score * score > threshold:
            max_sentence = sentence
            max_score = level_score * score
            max_level = level
    return max_level, max_sentence, max_score

def get_sentence_start_end(doc:str, sentence: str) -> tuple[int, int]:
    """
    :param doc: The document to search.
    :param sentence: The sentence to search for.

    Returns the start and end index of the sentence in the document.
    """
    start = doc.index(sentence)
    end = start + len(sentence)
    return start, end

@task
def search(
    doc: str, 
    case: Case,
    question_schema: Path, 
    categories_schema: Path, 
    threshold=0.1) -> Case:
    """
    Find the sentence which most matches the question and the category.

    :param doc: The document to search.
    :param case: The case to update.
    :param question_schema: The schema for the question.
    :param categories_schema: The schema for the categories.
    :param threshold: The threshold for filtering.

    :return: The updated case.
    """
    questions = load_schema(question_schema)
    categories = load_schema(categories_schema)
    for k in questions.keys():
        if categories[k] == "raw" or categories[k] == "continuous":
            continue
        doc_sims = doc_similarities(questions[k], doc)
        matched_level, matched_sentence, matched_score = match_levels(doc_sims, doc, categories[k], threshold)
        if matched_level:
            s_start, s_end = get_sentence_start_end(doc, matched_sentence)
            cf = CaseField(value=matched_level, confidence=matched_score, evidence=Evidence.from_character_startend(doc, s_start, s_end))
        else:
            cf = CaseField(value=categories[k][-1], confidence=0, evidence=Evidence.no_match())
        case.add_field(k, cf)
    return case
            


        
    