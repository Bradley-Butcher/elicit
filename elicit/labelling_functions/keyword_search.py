"""Script which searches for keywords (from a schema) in a document."""
from pathlib import Path
from typing import Dict, List

import spacy
from spacy.matcher import PhraseMatcher

from elicit.document import Document, DocumentField, Evidence
from elicit.utils.loading import load_schema
from elicit.pipeline import labelling_function


def exact_match_single(doc: str, keywords: Dict[str, List[str]]) -> List[DocumentField]:
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
    casefields = []
    for match in exact_matches.keys():
        casefields.append(DocumentField(value=match, confidence=1.0, evidence=Evidence.from_spacy_multiple(doc, exact_matches[match])))
    return casefields

@labelling_function(labelling_method="Keyword Match", required_schemas=["keyword_schema", "categories_schema"])
def exact_match(doc: str, document: Document, keyword_schema: Path, categories_schema: Path) -> Document:
    """
    Match the keywords in the document with the keywords in the keywords file.

    :param doc: The document to extract the keywords from.
    :param case: The case to add the keywords to.
    :param keyword_path: The path to the keywords file.
    :param categories_path: The path to the categories file.

    :return: The case with the keywords added.
    """
    field_keywords = load_schema(keyword_schema)
    categories = load_schema(categories_schema)
    for field in field_keywords.keys():
        match = exact_match_single(doc, field_keywords[field])
        if match:
            setattr(document, field, match)
        else:
            default_category = categories[field][-1]
            cf = DocumentField(value=default_category, confidence=0, evidence=Evidence.no_match())
            setattr(document, field, cf)
    return document
        
        
