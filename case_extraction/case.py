from pathlib import Path
from typing import Iterable, List, Literal, Optional, Set, Tuple, Union
from attr import asdict, dataclass
import pandas as pd
import spacy
from spacy.matcher import Matcher
from tqdm import tqdm

from case_extraction.defendants import extract_defendants_filename, extract_defendants_regex
from case_extraction.extraction import extract_variables
from case_extraction.qa_transformer import extract_answers
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


@dataclass
class Case:

    offenses: Union[str, Set[str]]
    premeditated: str
    weapon: Union[str, Set[str]]
    vulnerable_victim: str
    prior_convictions: str
    physical_abuse: str
    emotional_abuse: str
    age_mitigating: str
    race_aggrevating: str
    religious_aggrevating: str
    offender_confession: str
    victim_sex: Union[str, Set[str]]
    victim_age: Union[str, Set[str]]
    offender_age: Union[str, Set[str]]
    offender_sex: Union[str, Set[str]]
    relationship: Union[str, Set[str]]
    victims: Union[str, Set[str]]
    defendants: Union[str, Set[str]]
    outcome: Union[str, Set[str]]
    filename: Optional[str] = None
    doc: Optional[str] = None

    @classmethod
    def from_filename(cls, filename: Union[str, Path]):
        """
        Initializes a case object from a filename, loading the document, and extracting the relevant information.
        """
        filename = Path(filename)
        doc = pdf_to_plaintext(filename, newlines=False)
        defendants = list(Case.get_defendants(filename, doc))
        case = cls(**extract_variables(doc=doc, defendant=defendants[0]))
        case.filename = filename
        case.doc = doc
        return case

    @staticmethod
    def get_defendants(filename: Path, doc: str) -> Set[str]:
        """
        Gets the defendant names from the document or filename.
        """
        result = extract_defendants_filename(filename.stem)
        if not result:
            result = extract_defendants_regex(doc)
        return set(result)

    def extraction_performance(self, true: "Case") -> Tuple[float, str]:
        """
        Calculates the proportion of matching properties between two cases.
        """
        other_dict = true.to_dict()
        this_dict = self.to_dict()
        match_count = 0
        for k, v in other_dict.items():
            if not isinstance(v, set):
                v = set(v)
            if this_dict[k] in v:
                match_count += 1
        return match_count / len(other_dict), f"{match_count}/{len(other_dict)}"

    def __str__(self):
        if isinstance(self.defendants, set):
            return f"R v. {', '.join(self.defendants)}"
        else:
            return f"R v. {self.defendants}"

    def compare(self, true: "Case") -> dict[dict[str, str]]:
        return {f"{str(true)} Exctracted": self.to_dict(), f"{str(true)} True": true.to_dict()}

    def debug(self, true: "Case") -> dict[dict[str, str]]:
        answers = extract_answers(self.doc, threshold=0)
        return {f"{str(true)} Answers": answers, f"{str(true)} True": true.to_dict()}

    def to_dict(self):
        dont_return = ["filename", "doc"]
        return {k: v for k, v in asdict(self).items() if k not in dont_return}


def debug_table(cases: List[Case], pdf_dir: Path) -> pd.DataFrame:
    comparisons = {}
    for case in tqdm(cases, desc="Processing Cases", total=len(cases)):
        extracted_case = Case.from_filename(pdf_dir / case.filename)
        comparisons = {**comparisons, **extracted_case.debug(case)}
    return pd.DataFrame.from_dict(comparisons, orient='index')


def comparison_table(cases: List[Case], pdf_dir: Path) -> pd.DataFrame:
    comparisons = {}
    for case in tqdm(cases, desc="Processing Cases", total=len(cases)):
        extracted_case = Case.from_filename(pdf_dir / case.filename)
        comparisons = {**comparisons, **extracted_case.compare(case)}
    return pd.DataFrame.from_dict(comparisons, orient='index')


def performance_table(cases: List[Case], pdf_dir: Path) -> pd.DataFrame:
    performance = []
    for case in tqdm(cases, desc="Processing Cases", total=len(cases)):
        extracted_case = Case.from_filename(pdf_dir / case.filename)
        performance.append(
            {str(case): {"performance": extracted_case.extraction_performance(case)[1]}})
    return pd.DataFrame.from_dict(performance, orient='index')
