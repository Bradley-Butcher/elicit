from case_extraction.case import Case, Entity

import itertools
from typing import List, Tuple
from collections import Counter
import re

import spacy
import neuralcoref
from spacy.matcher import Matcher
from spaczz.matcher import FuzzyMatcher
from spacy import displacy
import opennre
import pandas as pd


def extract_mentioned_phrases(doc: str, phrase_list: List[str], threshold: float = 0.9, debug: bool = False) -> Counter:
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


def extract_instruments(doc: str) -> list:
    """
    Extracts the instruments from the document.
    """
    nlp = spacy.load("en_blackstone_proto")
    doc = nlp(doc)

    instruments = []
    for ent in doc.ents:
        if ent.label_ == "INSTRUMENT":
            instruments.append(ent.text)
    return instruments


def extract_entity_names(doc: str) -> list:
    """
    Extracts the names from the document.
    """
    nlp = spacy.load("en_core_web_md")
    doc = nlp(doc)

    names = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
    return names


def extract_names(doc: str) -> list:
    """
    Extracts the names from the document.
    """
    matches = re.findall(r".+ -v- (.+)\n", doc) + \
        re.findall(r".+ v (.+)\n", doc) + \
        re.findall(r".+\n-v- \n(.+)\n", doc) + \
        re.findall(r".+\nv \n(.+)\n", doc) + \
        re.findall(r".+\n(.+)\n-V- \n", doc)
    names = []
    for match in matches:
        match = match.strip()
        if "," in match:
            names += match.split(",")
        if "&" in match:
            names += match.split("&")
        else:
            names.append(match)
    names = filter(None, names)
    return [n.strip().title() for n in names]


def extract_offense(doc: str) -> str:
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
