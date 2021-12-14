from pathlib import Path
from typing import List, Set
from collections import Counter
import pandas as pd

import spacy


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


def update_readme(df: pd.DataFrame) -> None:
    base_path = Path(__file__).parent
    readme = base_path.parent / "README.md"
    with open(readme, "r") as f:
        lines = f.readlines()
    performance_line = 0
    for i, line in enumerate(lines):
        if line.startswith("## Current Performance"):
            performance_line = i + 1
            break
    new_md = df.to_markdown().split("\n")
    lines[performance_line: performance_line + len(new_md)] = new_md
    with open(readme, "w") as f:
        f.write("\n".join([l.replace("\n", "") for l in lines]))


def context_from_doc_char(doc: str, start_idx: int, end_idx: int, padding: int = 100) -> str:
    """
    Extracts the context from the document based on the start and end indices.
    """
    start_idx = max(0, start_idx - padding)
    end_idx = min(len(doc), end_idx + padding)
    return doc[start_idx: end_idx]