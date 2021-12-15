from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Literal, Optional, Set, Tuple, Union
import pandas as pd
import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from tqdm import tqdm

from case_extraction.utils.utils import context_from_doc_char


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

@dataclass
class Evidence:
    """
    Class for storing evidence.
    """
    local_context: str
    wider_context: str

    @classmethod
    def no_match(cls) -> "Evidence":
        """Returns an evidence object with no match."""
        return cls("N/A", "N/A")
    
    @classmethod
    def from_character_startend(cls, doc: str, start: int, end:int, local_padding: int = 100, wider_padding: int = 500) -> "Evidence":
        """
        Returns an evidence object from a character start and end index.
        """
        local_context = context_from_doc_char(doc, start, end, local_padding)
        wider_context = context_from_doc_char(doc, start, end, wider_padding)
        return cls(local_context, wider_context)
    
    @classmethod
    def from_spacy(cls, doc: Language, start: int, end:int, local_padding: int = 0, wider_padding: int = 10) -> "Evidence":
        """
        Returns an evidence object from a character start and end index.
        """
        local_context = doc[start:end]
        start = max(0, start - local_padding)
        end = min(len(doc), end + local_padding)
        wider_context = doc[start:end]
        return cls(local_context.text, wider_context.text)
    
    @classmethod
    def from_spacy_multiple(cls, doc: Language, evidence_list: List[Tuple[str, int, int]], wider_padding: int = 10) -> "Evidence":
        local_context = ", ".join([span for span, _, _ in evidence_list])
        widers = []
        for span, start, end in evidence_list:
            start = max(0, start - wider_padding)
            end = min(len(doc), end + wider_padding)
            widers.append(doc[start:end].text)
        wider_context = " | ".join(widers)
        return cls(local_context, wider_context)

class CaseField:
    def __init__(self, value: str, confidence: float, evidence: Evidence):
        self.value = value
        self.confidence = confidence
        self.evidence = evidence
    
    def __str__(self) -> str:
        return f"{self.value} ({self.confidence})"
    
    def __mul__(self, other: float) -> float:
        return self.confidence * other
    
    def __rmul__(self, other: float) -> float:
        return self.confidence * other
    
    def __add__(self, other: Union["CaseField", list]) -> List["CaseField"]:
        if isinstance(other, CaseField):
            return [self, other]
        elif isinstance(other, list):
            return [self] + other
        else:
            raise TypeError(f"Cannot add {type(other)} to CaseField")
    
    def __radd__(self, other: Union["CaseField", list]) -> List["CaseField"]:
        if isinstance(other, CaseField):
            return [self, other]
        elif isinstance(other, list):
            return [self] + other
        else:
            raise TypeError(f"Cannot add {type(other)} to CaseField")
    
    

class Case:

    def __init__(self, filename: str, method: str, **kwargs):
        self.filename = filename
        self.method = method
        self.__dict__.update(kwargs)
        
    def add_dict(self, dict_to_add: dict):
        for key, value in dict_to_add.items():
            if not hasattr(self, key):
                setattr(self, key, value)
            else:
                current = getattr(self, key)
                if isinstance(value, CaseField):
                    value = [value]
                setattr(self, key, current + value)
                
    @classmethod
    def manual_entry(cls, filename: Union[str, Path], **kwargs):
        """
        Class method for creating a case object using direct input for test cases.
        """
        for key, value in kwargs.items():
            if isinstance(value, list) or isinstance(value, set):
                kwargs[key] = [CaseField(value=v, confidence=1, evidence="") for v in value]
            else:
                kwargs[key] = CaseField(value=value, confidence=1, evidence="")
        return cls(filename=filename, method="manual", **kwargs)
    
    @staticmethod
    def to_variables(variable_dict: Dict[str, Tuple[str, float]]) -> Dict[str, CaseField]:
        return {k: CaseField(value=v[0], confidence=v[1]) for k, v in variable_dict.items()}

    def extraction_performance(self, true: "Case") -> Tuple[float, str]:
        """
        Calculates the proportion of matching properties between two cases.
        """
        other_dict = true.to_dict()
        this_dict = self.to_dict()
        match_count = 0
        for k, v in other_dict.items():
            if isinstance(v, str):
                v = {v}
            if isinstance(v, list):
                v = set(v)
            if str(this_dict[k]).lower() in v:
                match_count += 1
        return match_count / len(other_dict), f"{match_count}/{len(other_dict)}"

    def __str__(self):
        if isinstance(self.defendants, Iterable):
            return f"R v. {', '.join([d.value for d in self.defendants])}"
        else:
            return f"R v. {self.defendants.value}"

    def compare(self, true: "Case") -> dict[dict[str, str]]:
        return {f"{str(true)} Extracted": self.to_printable_dict(), f"{str(true)} True": true.to_printable_dict()}

    def to_printable_dict(self) -> dict[str, str]:
        output = self.to_dict()
        for k, v in output.items():
            if isinstance(v, list):
                output[k] = ", ".join([str(vi) for vi in v])
            if isinstance(v, CaseField):
                output[k] = str(v)
        return output

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if isinstance(v, CaseField) or isinstance(v, list)}