import pytest
from pathlib import Path

from case_extraction.load import pdf_to_plaintext, load_offense_list, load_instrument_list
from case_extraction.extraction import is_remarks, is_appeal, extract_mentioned_phrases, extract_names, extract_entity_names


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


def test_extract_manslaughter():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Anthony_Williams_sentencing_remarks.pdf'
    text = pdf_to_plaintext(pdf_path)
    offense_list = load_offense_list()
    offenses = extract_mentioned_phrases(text, offense_list)
    assert offenses.most_common()[0][0] == 'Manslaughter'


def test_extract_murder():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Gazeley.pdf'
    text = pdf_to_plaintext(pdf_path)
    offense_list = load_offense_list()
    offenses = extract_mentioned_phrases(text, offense_list)
    assert offenses.most_common()[0][0] == 'Murder'


def test_computer_misuse():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_James_Jeffery.pdf'
    text = pdf_to_plaintext(pdf_path)
    instrument_list = load_offense_list()
    offenses = extract_mentioned_phrases(text, offense_list)
    assert offenses.most_common()[0][0] == 'Computer Misuse'


def test_child_abuse():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Jeremy_Forrest.pdf'
    text = pdf_to_plaintext(pdf_path)
    offense_list = load_offense_list()
    offenses = extract_mentioned_phrases(text, offense_list, debug=True)
    assert offenses.most_common()[0][0] == 'Murder'


def test_by_dangerous_driving():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Kowalczyk_and_others.pdf'
    text = pdf_to_plaintext(pdf_path)
    offense_list = load_offense_list()
    offenses = extract_mentioned_phrases(text, offense_list)
    assert offenses.most_common()[0][0] == 'Dangerous driving'


def test_extract_names():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_v_Gary_Dobson_and_David_Norris.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0], raw=True)
    names = extract_names(text)
    assert names == ['Dobson', 'Norris']


def test_extract_names_2():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Bradbury.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0], raw=True)
    names = extract_names(text)
    assert names == ["Myles James Edward Bradbury"]


def test_extract_names_3():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Amanda_Hutton_and_Tariq_Khan.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0], raw=True)
    names = extract_names(text)
    assert names == ["Amanda Hutton", "Tariq Khan"]
