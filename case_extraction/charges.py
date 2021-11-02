import re

from case_extraction.utils import fuzzy_phrases
from case_extraction.loading import load_offense_list


def extract_offenses_regex(doc: str) -> str:
    """
    Extracts the offense from the document.
    """
    matches = re.findall(r".+ -v- (.+)\n", doc)
    offenses = []
    for match in matches:
        match = match.strip()
        if "," in match:
            offenses += match.split(",")
        if "&" in match:
            offenses += match.split("&")
        else:
            offenses.append(match)
    offenses = filter(None, offenses)
    return [n.strip().title() for n in offenses]


def extract_offenses_matched(doc: str, threshold: float = 0.85) -> str:
    """
    Extracts the offenses from the document by (fuzzily) comparing to a list of offenses.
    """

    return fuzzy_phrases(doc, load_offense_list(), threshold).keys()
