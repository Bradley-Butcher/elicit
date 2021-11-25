from pathlib import Path
from typing import Callable, Dict, Iterable, List, Literal, Optional, Set, Tuple, Union
import pandas as pd
import spacy
from spacy.matcher import Matcher
from tqdm import tqdm

from case_extraction.components.qa_transformer import extract_answers


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


class CaseField:
    def __init__(self, value: str, confidence: float, evidence: str):
        self.value = value
        self.confidence = confidence
        self.evidence = evidence
    
    def __str__(self) -> str:
        return f"{self.evidence} ({self.value}, {self.confidence})"
    
    def __mul__(self, other: float) -> float:
        return self.confidence * other
    
    def __rmul__(self, other: float) -> float:
        return self.confidence * other

class Case:

    def __init__(self, filename: str, method: str, **kwargs):
        self.filename = filename
        self.method = method
        self.__dict__.update(kwargs)
        
    def add_dict(self, dict_to_add: dict):
        for key, value in dict_to_add.items():
            dict_to_add[key] = CaseField(value=value[0], confidence=value[1], evidence="")
        self.__dict__.update(dict_to_add)

    @classmethod
    def manual_entry(cls, filename: Union[str, Path], **kwargs):
        """
        Class method for creating a case object using direct input for test cases.
        """
        for key, value in kwargs.items():
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
        if isinstance(self.defendants, set):
            return f"R v. {', '.join(self.defendants.value)}"
        else:
            return f"R v. {self.defendants.value}"

    def compare(self, true: "Case") -> dict[dict[str, str]]:
        return {f"{str(true)} Extracted": self.to_dict(), f"{str(true)} True": true.to_dict()}

    def debug(self, true: Optional["Case"]) -> dict[dict[str, str]]:
        answers = extract_answers(self.doc, threshold=0)
        if not true:
            return {f"{str(self)}": answers}
        return {f"{str(true)} Answers": answers, f"{str(true)} True": true.to_dict()}

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if isinstance(v, CaseField)}



# def debug_table(cases: List[Case], pdf_dir: Path, question_schema: Path, category_schema: Path) -> pd.DataFrame:
#     comparisons = {}
#     for case in tqdm(cases, desc="Processing Cases", total=len(cases)):
#         extracted_case = Case.from_filename(pdf_dir / case.filename, categories_schema=category_schema, question_schema=question_schema)
#         comparisons = {**comparisons, **extracted_case.debug(case)}
#     return pd.DataFrame.from_dict(comparisons, orient='index')

# def performance_table(cases: List[Case], pdf_dir: Path, question_schema: Path, category_schema: Path) -> pd.DataFrame:
#     performance = {}
#     for case in tqdm(cases, desc="Processing Cases", total=len(cases)):
#         extracted_case = Case.from_filename(pdf_dir / case.filename, categories_schema=category_schema, question_schema=question_schema)
#         p = {
#             str(case): {"Correctly Extracted Variables": extracted_case.extraction_performance(case)[1]}}
#         performance = {**performance, **p}
#     return pd.DataFrame.from_dict(performance, orient='index')
