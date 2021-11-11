import re
from typing import Dict, Set, Tuple

from spacy.language import Language
from spacy.tokens import Doc

from case_extraction.loading import load_offense_list

import spacy
from spacy.language import Language
from spacy.matcher import DependencyMatcher
import holmes_extractor as holmes


def extract_conviction_patterns(doc: str) -> Set[str]:
    """
    Extract convictions from the document using a dependency matcher.
    """
    nlp = spacy.load("en_core_web_sm")
    matcher = DependencyMatcher(nlp.vocab)
    doc = nlp(doc)
    pattern_1 = [
        {
            "RIGHT_ID": "convicted",
            "RIGHT_ATTRS": {"LOWER": "convicted"}
        },
        {
            "LEFT_ID": "convicted",
            "REL_OP": ">",
            "RIGHT_ID": "prep",
            "RIGHT_ATTRS": {"DEP": "prep"}
        },
        {
            "LEFT_ID": "prep",
            "REL_OP": ">",
            "RIGHT_ID": "conviction_offense",
            "RIGHT_ATTRS": {"DEP": "pobj", "POS": "NOUN"}
        }
    ]
    trick_nouns = ["count", "offence", "offences"]
    matcher.add("CONVICTION", [pattern_1])
    matched_convictions = []
    matches = matcher(doc)
    for _, token_ids in matches:
        if doc[token_ids[-1]].text not in trick_nouns:
            matched_convictions.append(doc[token_ids[-1]].text)
    return set(matched_convictions)


def extract_plea_patterns(doc: str) -> Set[Tuple[str, str]]:
    """
    Extract a list of pleas from the document using a dependency matcher.
    """
    nlp = spacy.load("en_core_web_sm")
    matcher = DependencyMatcher(nlp.vocab)
    doc = nlp(doc)
    pattern_1 = [
        {
            "RIGHT_ID": "plea",
            "RIGHT_ATTRS": {"LOWER": "pleaded"}
        },
        {
            "LEFT_ID": "plea",
            "REL_OP": ">",
            "RIGHT_ID": "plea_status",
            "RIGHT_ATTRS": {"DEP": "acomp"}
        },
        {
            "LEFT_ID": "plea_status",
            "REL_OP": ">",
            "RIGHT_ID": "prep",
            "RIGHT_ATTRS": {"DEP": "prep"}
        },
        {
            "LEFT_ID": "prep",
            "REL_OP": ">",
            "RIGHT_ID": "plea_offense",
            "RIGHT_ATTRS": {"DEP": "pobj", "POS": "NOUN"}
        }
    ]
    pattern_2 = [
        {
            "RIGHT_ID": "plea",
            "RIGHT_ATTRS": {"LOWER": "pleaded"}
        },
        {
            "LEFT_ID": "plea",
            "REL_OP": ">",
            "RIGHT_ID": "plea_status",
            "RIGHT_ATTRS": {"DEP": "acomp"}
        },
        {
            "LEFT_ID": "plea_status",
            "REL_OP": ">",
            "RIGHT_ID": "prep",
            "RIGHT_ATTRS": {"DEP": "prep"}
        },
        {
            "LEFT_ID": "prep",
            "REL_OP": ">",
            "RIGHT_ID": "count",
            "RIGHT_ATTRS": {"DEP": "pobj", "POS": "NOUN"}
        },
        {
            "LEFT_ID": "count",
            "REL_OP": "<",
            "RIGHT_ID": "count_num",
            "RIGHT_ATTRS": {"DEP": "nummod", "POS": "NUM"}
        },
        {
            "LEFT_ID": "count",
            "REL_OP": ">",
            "RIGHT_ID": "prep2",
            "RIGHT_ATTRS": {"DEP": "prep"}
        },
        {
            "LEFT_ID": "prep2",
            "REL_OP": ">",
            "RIGHT_ID": "plea_offense",
            "RIGHT_ATTRS": {"DEP": "pobj", "POS": "NOUN"}
        },
    ]
    matcher.add("PLEA", [pattern_1, pattern_2])
    matched_convictions = []
    matches = matcher(doc)
    trick_nouns = ["count", "offence", "offences"]
    for _, token_ids in matches:
        plea = token_ids[1]
        offense = token_ids[-1]
        if doc[offense].text not in trick_nouns:
            matched_convictions.append((doc[offense].text, doc[plea].text))
    return set(matched_convictions)


@Language.component("extract_offenses")
def extract_offenses(doc: Language):
    Doc.set_extension("offenses", default=[])
    offences = load_offense_list()
    found_offenses = []
    for chunk in doc.noun_chunks:
        for offence in offences:
            if str(chunk) == offence:
                head = chunk.root.head
                if head.pos_ == "VERB":
                    found_offenses.append(offence)
    doc._.offenses = found_offenses
    return doc


def offense_focused_extraction(doc: str) -> Set[str]:
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("merge_entities")
    nlp.add_pipe("merge_noun_chunks")
    nlp.add_pipe("extract_offenses")
    doc = nlp(doc)
    # matcher = DependencyMatcher(nlp.vocab)
    # doc = nlp(doc)
    # patterns = []
    # for offence in offences:
    #     patterns.append(
    #         [
    #             {
    #                 "RIGHT_ID": "verb",
    #                 "RIGHT_ATTRS": {"POS": "VERB"}
    #             },
    #             {
    #                 "LEFT_ID": "verb",
    #                 "REL_OP": ">>",
    #                 "RIGHT_ID": "offence",
    #                 "RIGHT_ATTRS": {"LOWER": offence.lower()}
    #             }],
    #     )
    # matcher.add("OFFENCE", patterns)
    # matched_convictions = []
    # matches = matcher(doc)
    # for _, token_ids in matches:
    #     offense = token_ids[-1]
    #     matched_convictions.append(doc[offense].text)
    return set(doc._.offenses)


def extract_charges(doc: str) -> Dict[str, Set[str]]:
    return {
        "conviction": extract_conviction_patterns(doc),
        "plea": extract_plea_patterns(doc),
        "offence": offense_focused_extraction(doc)
    }
