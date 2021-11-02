from pathlib import Path
from typing import List, Set
import spacy
from spacy.matcher import Matcher

from case_extraction.defendants import extract_defendants_filename, extract_defendants_regex
from case_extraction.charges import extract_offenses_matched
from case_extraction.loading import pdf_to_plaintext


def is_remarks(doc: str, filename: str) -> str:
    """
    Extracts the type of the case from the document.
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
    Extracts the type of the case from the document.
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


class Case:
    """
    Class representing a case.
    Contains:
    - List of Defendants
    - List of Victims
    - List of Charges
    - List of Mitigating Circumstances
    - List of Aggravating Circumstances
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.doc = pdf_to_plaintext(filename)
        self.defendants = self.get_defendants()
        self.victims = self.get_victims()
        self.charges = self.get_charges()
        self.mitigating_circumstances = self.get_mitigating_circumstances()
        self.aggravating_circumstances = self.get_aggravating_circumstances()

    @classmethod
    def manual_entry(
        cls,
        filename: str,
        defendants: List[str],
        victims: List[str],
        charges: List[str],
        mitigating_circumstances: List[str],
        aggravating_circumstances: List[str],
    ) -> Case:   # type: ignore
        """
        Manual entry of case details.
        """
        return cls(filename, defendants, victims, charges, mitigating_circumstances, aggravating_circumstances)

    def get_defendants(self) -> Set[str]:
        if self.defendants is not None:
            return self.defendants
        result = extract_defendants_filename(self.filename)
        if not result:
            result = extract_defendants_regex(self.doc)
        return set(result)

    def get_victims(self) -> list:
        pass

    def get_charges(self) -> List[str]:
        if self.charges is not None:
            return self.charges
        return extract_offenses_matched

    def get_mitigating_circumstances(self) -> list:
        pass

    def get_aggravating_circumstances(self) -> list:
        pass

    def compare(self, other: Case):  # type: ignore
        """
        Compares two cases.
        """
        d1 = self.get_defendants()
        d2 = other.get_defendants()
        defendent_hamming = len(d1.symmetric_difference(d2))

        c1 = self.get_charges()
        c2 = other.get_charges()
        charge_hamming = len(c1.symmetric_difference(c2))
        return {"defendants": defendent_hamming,
                "charges": charge_hamming}
