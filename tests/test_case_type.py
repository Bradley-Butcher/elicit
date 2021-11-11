import pytest
from pathlib import Path

from case_extraction.loading import pdf_to_plaintext, load_offense_list, load_instrument_list
from case_extraction.case import is_remarks, is_appeal


def test_is_remarks():
    pdf_path = Path(__file__).parent.parent / "pdfs" / \
        "crown court" / "R_-v-_Jewell_and_Others.pdf"
    text = pdf_to_plaintext(pdf_path, pages=[0])
    assert is_remarks(text, pdf_path.stem)


def test_negative_is_appeal():
    pdf_path = Path(__file__).parent.parent / "pdfs" / \
        "crown court" / "R_-v-_Jewell_and_Others.pdf"
    text = pdf_to_plaintext(pdf_path, pages=[0])
    assert not is_appeal(text, pdf_path.stem)


def test_is_appeal():
    pdf_path = Path(__file__).parent.parent / \
        'pdfs' / "court of appeal" / \
        'R_-v-_Scott_Crawley,_Dale_Walker,__Daniel_Forsyth,_Aaron_Petrou_and_Brendan_Daley.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0])
    assert is_appeal(text, pdf_path.stem)
