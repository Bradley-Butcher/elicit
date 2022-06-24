"""Script to test the case module."""
from elicit.interface import Extraction


def test_no_extract_match():
    """
    Tests that the case_extraction.case.extraction class can handle no extract.
    """
    extract = Extraction.abstain()
    assert extract.value == "ABSTAIN"
    assert extract.exact_context == None
    assert extract.local_context == None
    assert extract.wider_context == None


def test_extract_from_char_startend():
    """
    Tests that the case_extraction.case.extraction class can handle extract from a character start and end index.
    """
    extract = Extraction.from_character_startend(
        "This is a test", "test", 1, 0, 10)
    assert extract.value == "test"
    assert extract.exact_context == "This is a"
    assert extract.local_context == "This is a test"
    assert extract.wider_context == "This is a test"


def test_extract_from_spacy():
    """
    Tests that the case_extraction.case.extraction class can handle extract from a spacy object.
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test")
    extract = Extraction.from_spacy(doc, "test", 1, 0, 3)
    assert extract.value == "test"
    assert extract.exact_context == "This is a"
    assert extract.local_context == "This is a"
    assert extract.wider_context == "This is a test"


def test_extract_from_spacy_multiple():
    """
    Tests that the case_extraction.case.extraction class can handle extract from multiple spacy objects.
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test")
    extract = Extraction.from_spacy_multiple(
        doc, "test", 1, [("This", 0, 1), ("test", 4, 4)])
    assert extract.exact_context == "This, test"
    assert extract.local_context == "This, test"
    assert extract.wider_context == "This is a test | This is a test"
