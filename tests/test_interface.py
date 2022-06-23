"""Script to test the case module."""
from elicit.interface import Extraction


def test_no_evidence_match():
    """
    Tests that the case_extraction.case.Evidence class can handle no evidence.
    """
    evidence = Extraction.abstain()
    assert evidence.exact_context == "ABSTAIN"
    assert evidence.local_context == None
    assert evidence.wider_context == None


def test_evidence_from_char_startend():
    """
    Tests that the case_extraction.case.Evidence class can handle evidence from a character start and end index.
    """
    evidence = Extraction.from_character_startend("This is a test", 0, 10)
    assert evidence.exact_context == "This is a"
    assert evidence.local_context == "This is a test"
    assert evidence.wider_context == "This is a test"


def test_evidence_from_spacy():
    """
    Tests that the case_extraction.case.Evidence class can handle evidence from a spacy object.
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test")
    evidence = Extraction.from_spacy(doc, 0, 3)
    assert evidence.exact_context == "This is a"
    assert evidence.local_context == "This is a"
    assert evidence.wider_context == "This is a test"


def test_evidence_from_spacy_multiple():
    """
    Tests that the case_extraction.case.Evidence class can handle evidence from multiple spacy objects.
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test")
    evidence = Extraction.from_spacy_multiple(
        doc, [("This", 0, 1), ("test", 4, 4)])
    assert evidence.exact_context == "This, test"
    assert evidence.local_context == "This, test"
    assert evidence.wider_context == "This is a test | This is a test"
