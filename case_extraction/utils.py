from typing import List, Set
from collections import Counter

from spaczz.matcher import FuzzyMatcher
import spacy


def fuzzy_phrases(doc: str, phrase_list: List[str], threshold: float = 0.9, debug: bool = False) -> Counter:
    """
    Extracts the mentioned phrases from the document.
    """
    nlp = spacy.load("en_core_web_sm")
    matcher = FuzzyMatcher(nlp.vocab)

    for phrase in list(set(phrase_list)):
        matcher.add(phrase, [nlp(phrase)])

    doc = nlp(doc)
    matches = matcher(doc)

    mentioned_phrases = []

    for match_id, start, end, ratio in matches:
        if debug:
            mentioned_phrases.append([match_id, doc[start:end], ratio])
        else:
            if (ratio / 100) > threshold:
                mentioned_phrases.append(match_id)
    if not debug:
        return Counter(mentioned_phrases)
    else:
        return mentioned_phrases


def extract_entities(doc: str, entity_types: Set[str] = {"PERSON"}) -> list:
    """
    Extracts the names from the document.
    """
    nlp = spacy.load("en_core_web_md")
    doc = nlp(doc)

    names = []
    for ent in doc.ents:
        if ent.label_ in entity_types:
            names.append(ent.text)
    return names
