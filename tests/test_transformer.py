from pathlib import Path
import pytest
from case_extraction.defendants import extract_defendants_filename
from case_extraction.loading import pdf_to_plaintext
from case_extraction.qa_transformer import extract_answers
from case_extraction.extraction import extract_variables

crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"


def _get_examples():
    return [
        "R_-v-_Colin_Ash-Smith.pdf",
        "R_-v-_Adam_Lewis.pdf",
        "R_-v-_Benjamin_Curtis.pdf",
        "R_-v-_Barysaite_and_Jakimovas_sentencing_remarks.pdf",
        "Sentencing_remarks_of_His_Honour_Judge_Eccles_Q.C.:_R_-v-_Ben_Blakeley.pdf"
    ]


@pytest.mark.parametrize("filename", _get_examples())
def test_transformer_simple_qa(filename: str):
    pdf_path = crown_court_path / filename
    case = pdf_to_plaintext(pdf_path, newlines=False)
    defendants = extract_defendants_filename(pdf_path.name)
    answers = extract_variables(case, defendant=defendants[0])
    assert answers
