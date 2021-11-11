from pathlib import Path
from typing import Set
import pytest

from case_extraction.case import Case
from case_extraction.charges import extract_charges, offense_focused_extraction
from case_extraction.loading import pdf_to_plaintext

from .example_cases import load_train_cases

crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"


def _get_examples():
    return [
        ("R_-v-_Colin_Ash-Smith.pdf", "conviction", {"murder"}),
        ("R_-v-_Adam_Lewis.pdf", "plea", {("murder", "guilty")}),
        ("R_-v-_Benjamin_Curtis.pdf", "plea", {"manslaughter"}),
        ("R_-v-_Barysaite_and_Jakimovas_sentencing_remarks.pdf",
         "offence", {"murder"})
    ]


@pytest.mark.parametrize("filename, charge_type, true_charges", _get_examples())
def test_charge_extraction(filename: str, charge_type: str, true_charges: Set[str]):
    pdf_path = crown_court_path / filename
    case = pdf_to_plaintext(pdf_path, newlines=False)
    extracted_charges = extract_charges(case)
    for k, v in extracted_charges.items():
        if k == charge_type:
            assert v
        else:
            assert not v
    assert true_charges - extracted_charges[charge_type] == set()


def test_offense_focused_extraction():
    text = "You have pleaded guilty to an offence of false accounting which encompasses"
    match = offense_focused_extraction(text)
    assert match == {"false accounting"}
