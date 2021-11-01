import pytest
from pathlib import Path
from case_extraction.load import load_pdf, pdf_to_plaintext


def test_load_pdf():
    """
    Test loading of a pdf file.
    """
    pdf_path = Path(__file__).parent.parent / 'pdfs' / 'A_-v-_R.pdf'
    text = load_pdf(pdf_path)
    assert len(text) > 0


def test_pdf_processing():
    """
    Test processing of a pdf file.
    """
    pdf_path = Path(__file__).parent.parent / 'pdfs' / \
        'Muhammed_Asif_-v-_Adil_Iqbal_Ditta_and_Noreen_Riaz_(CoA_Criminal_Division_judgment).pdf'
    text = pdf_to_plaintext(pdf_path)
    assert "\xa0" not in text
