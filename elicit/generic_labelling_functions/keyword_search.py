"""Script which searches for keywords (from a schema) in a document."""
from pathlib import Path
from typing import Dict, List, Tuple

import spacy
from spacy.matcher import PhraseMatcher

from elicit.interface import CategoricalLabellingFunction, Extraction


def exact_match(doc: str, keywords: Dict[str, List[str]]) -> List[Tuple[str, Extraction]]:
    """
    Extracts the keywords from the document for a single field.

    :param doc: The document to extract the keywords from.
    :param keywords: The keywords to search for. Form is: {field: [keywords]}

    :return: A list of CaseFields.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(doc)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for k in keywords.keys():
        patterns = [nlp.make_doc(text) for text in keywords[k]]
        matcher.add(k, patterns)
    matches = matcher(doc)
    exact_matches = {}
    for match_id, start, end in matches:
        match = doc.vocab.strings[match_id]
        span = doc[start:end]
        if match not in exact_matches:
            exact_matches[match] = [(span.text, start, end)]
        else:
            exact_matches[match] += [(span.text, start, end)]
    extractions = []
    for match in exact_matches.keys():
        extractions.append(Extraction.from_spacy_multiple(
            doc=doc, value=match, confidence=1.0, evidence_list=exact_matches[match]))
    return extractions


class KeywordMatchLF(CategoricalLabellingFunction):
    """
    Labelling function which searches for keywords (from a schema) in a document.
    """

    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)

    def extract(self, document_name: str, variable_name: str, document_text: str) -> str:
        matches = exact_match(
            document_text,
            self.get_schema("keywords", variable_name)
        )
        self.push_many(document_name, variable_name, matches)

    @property
    def labelling_method(self):
        return "Keyword Match"

    def train(self, data: dict[str, List["Extraction"]]):
        pass

    def load(self, model_path: Path, device: str):
        self.loaded = True
        pass
