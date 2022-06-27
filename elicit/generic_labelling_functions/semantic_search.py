"""Script to extract answers from a document using a Sentence Similarity Transformer model trained on Q&A pairs."""
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from elicit.interface import CategoricalLabellingFunction, Extraction

def sentence_similarities(queries: list[str], sentences: list[str], model: SentenceTransformer, k: int = 5) -> dict[str, float]:
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

def doc_similarities(queries: list[str], doc: str, model: SentenceTransformer) -> dict[str, float]:
    """
    :param query: The query to compare to the document.
    :param doc: The document to compare to the query.

    Returns the most similar sentence and its similarity score.
    """
    sentences = doc.split(".") # should find a better way to split sentences - this is very basic
    return sentence_similarities(queries, sentences, model)


def match_levels(sentence_score: dict[str, float], levels: list[str], model: SentenceTransformer, threshold: float) -> tuple[str, str, float]:
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
        level, level_score = sentence_similarities([sentence], levels, model, k=1).popitem()
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
            

class SemanticSearchLF(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)
        self.sim_threshold = 0.25
    
    def load(self) -> None:
        self.model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1', device="cuda")

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)
        doc_sims = doc_similarities(questions, document_text, self.model)
        matched_level, matched_sentence, matched_score = match_levels(doc_sims, categories, self.model, self.sim_threshold)
        if matched_level:
            s_start, s_end = get_sentence_start_end(document_text, matched_sentence)
            self.push(document_name, variable_name, Extraction.from_character_startend(document_text, matched_level, matched_score, s_start, s_end))

    def train(self, document_name: str, variable_name: str, extraction: Extraction):
        pass

    @property
    def labelling_method(self) -> str:
        return "Semantic Search"
        
    