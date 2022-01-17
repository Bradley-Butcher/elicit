"""Script which extracts the defendants' names using various methods."""
import itertools
from pathlib import Path
from typing import List, Set
import re

from prefect import task

from elicit.case import Case, CaseField, Evidence


def _flatten(l: List[List[str]]) -> List[str]:
    """
    Flattens a list of lists into a single list.

    :param l: The list of lists to flatten.
    """
    if isinstance(l[0], str):
        return l
    return list(itertools.chain.from_iterable(l))


def extract_defendants_filename(filename: str) -> List[str]:
    """
    Extracts the defendents' names from the filename.

    :param filename: The filename to extract the names from.
    """
    splitter = None
    if "_v_" in filename.lower():
        splitter = "_v_"
    elif "_-v-_" in filename.lower():
        splitter = "_-v-_"
    if splitter is None:
        return []

    filename_rhs = filename.split(splitter)[-1]
    names = filename_rhs.split(",")
    names = _flatten([n.split("and") for n in names])
    names = _flatten([n.split(":")[0] for n in names])
    names = [n.replace("_", " ").strip().lower() for n in names]
    names = [n.replace(".pdf", "") for n in names]
    return names


def extract_defendants_regex(doc: str) -> List[str]:
    """
    Extracts the names from the document.

    :param doc: The document to extract the names from.
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
    return [n.strip().lower() for n in names]

@task
def get_defendants(filename: Path, doc: str, case: Case) -> Case:
    """
    Gets the defendant names from the document or filename.
    Adds the extracted names to the passed case object.

    :param filename: The filename to extract the names from.
    :param doc: The document to extract the names from.
    :param case: The case to add the names to.
    """
    result = extract_defendants_filename(filename.stem)
    if not result:
        result = extract_defendants_regex(doc)
    case.defendants =  CaseField(value=result[0], confidence=1.0, evidence=Evidence(exact_context=str(filename.stem), local_context=str(filename.name), wider_context=str(filename.name)))
    return case