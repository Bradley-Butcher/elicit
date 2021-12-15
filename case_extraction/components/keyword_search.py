from pathlib import Path
from typing import Dict, List, Tuple, Union
from spacy.language import Language

import yaml
import spacy
from spacy.matcher import PhraseMatcher
from prefect import task

from case_extraction.case import Case, CaseField, Evidence

def load_keywords(kw_path: Path) -> Dict[str, Union[str, List[str]]]:
    """
    Load the keywords from the YAML file.
    """
    with open(kw_path, "r") as f:
        return yaml.safe_load(f)


def exact_match_single(doc: str, case: Case, keywords: Dict[str, Dict[str, List[str]]]) -> List[CaseField]:
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
        casefields.append(CaseField(value=match, confidence=1.0, evidence=Evidence.from_spacy_multiple(doc, exact_matches[match])))
    return casefields

@task
def exact_match(doc: str, case: Case, keyword_path: Path) -> Case:
    """
    Match the keywords in the document with the keywords in the keywords file.
    """
    field_keywords = load_keywords(keyword_path)
    for field in field_keywords.keys():
        match = exact_match_single(doc, case, field_keywords[field])
        if match:
            setattr(case, field, match)
    return case
        
        
