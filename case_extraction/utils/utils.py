"""Script containing various utility functions."""
from pathlib import Path
from typing import List, Set
from collections import Counter
import pandas as pd
from spacy.matcher import Matcher

import spacy


def context_from_doc_char(doc: str, start_idx: int, end_idx: int, padding: int = 100) -> str:
    """
    Extracts the context from the document based on the start and end indices.

    :param doc: The document.
    :param start_idx: The start index.
    :param end_idx: The end index.
    :param padding: The padding to add to the start and end indices.

    :return: The context as a string.
    """
    start_idx = max(0, start_idx - padding)
    end_idx = min(len(doc), end_idx + padding)
    return doc[start_idx: end_idx]

def is_remarks(doc: str, filename: str) -> str:
    """
    Extracts whether the document is sentencing remarks.

    :param doc: The document.
    :param filename: The filename.

    :return: The type of the case.
    """
    if "sentencing_remarks" in filename.lower():
        return True
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(doc)

    sentence_pattern = [{"LOWER": "sentencing"},  {"LOWER": "remarks"}]

    matcher = Matcher(nlp.vocab)
    matcher.add("SR", None, sentence_pattern)

    matches = matcher(doc)

    if len(matches) > 0:
        return True
    else:
        return False


def is_appeal(doc: str, filename: str) -> str:
    """
    Extracts the type of the case is from the court of appeal.

    :param doc: The document.
    :param filename: The filename.

    :return: The type of the case.
    """
    if "court_of_appeal" in filename.lower():
        return True
    if "crown_court" in filename.lower():
        return False
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(doc)

    appeal = [{"LOWER": "court"}, {
        "LOWER": "of"}, {"LOWER": "appeal"}]

    crown = [{"LOWER": "crown"}, {"LOWER": "court"}]

    matcher = Matcher(nlp.vocab)
    matcher.add("APPEAL", None, appeal)
    matcher.add("CROWN", None, crown)

    matches = matcher(doc)

    if len(matches) > 0 and nlp.vocab.strings[matches[0][0]] == "APPEAL":
        return True
    return False