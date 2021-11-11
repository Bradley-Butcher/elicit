import pytest
from pathlib import Path
from case_extraction.loading import load_pdf, pdf_to_plaintext


def test_load_pdf():
    """
    Test loading of a pdf file.
    """
    pdf_path = Path(__file__).parent.parent / 'pdfs' / \
        "crown court" / 'R_-v-_Abdulrahman.pdf'
    text = load_pdf(pdf_path)
    assert len(text) > 0


def test_pdf_processing():
    """
    Test processing of a pdf file.
    """
    pdf_path = Path(__file__).parent.parent / 'pdfs' / \
        "crown court" / 'R_-v-_Abdulrahman.pdf'
    text = load_pdf(pdf_path)
    assert "\xa0" not in text
