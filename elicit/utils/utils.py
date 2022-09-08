"""Script containing various utility functions."""
import functools
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Set
from collections import Counter
import warnings


import pandas as pd
from spacy.matcher import Matcher
import spacy


def split_doc(doc: str, max_length: int = 512, token: str = ".") -> list:
    """Split a document into sentences.
    Splitting on the last period <Token> before the max length.

    Args:
        doc (str): Document to split.
        max_length (int): Maximum length of each sentence.

    Returns:
        list: List of sentences.
    """
    sections = []
    current_end = 0
    while current_end <= len(doc):
        if current_end + max_length >= len(doc):
            sections.append(doc[current_end:])
            break
        section_end = doc[current_end:current_end +
                          max_length].rfind(token) + current_end
        sections += [doc[current_end:section_end]]
        current_end = section_end
    return sections


def context_from_doc_char(doc: str, start_idx: int, end_idx: int, padding: int = 100) -> str:
    """
    Extracts the context from the document based on the start and end indices.

    :param doc: The document.
    :param start_idx: The start index.
    :param end_idx: The end index.
    :param padding: The padding to add to the start and end indices.

    :return: The context as a string.
    """
    if padding == 0:
        return doc[start_idx:end_idx]
    start_idx = max(0, start_idx - (padding // 2))
    end_idx = min(len(doc), end_idx + (padding // 2))

    start_idx = max([idx for idx in [doc[:start_idx].rfind(s)
                    for s in [".", ",", "\n"]]]) + 1
    end_idx = min([len(doc), *[idx + end_idx for idx in [doc[end_idx:].find(s) for s in [".", ",", "\n"]] if idx != 0]])

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
