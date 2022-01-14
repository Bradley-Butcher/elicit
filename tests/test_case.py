"""Script to test the case module."""
import pytest

from case_extraction.case import Evidence

def test_no_evidence_match():
    """
    Tests that the case_extraction.case.Evidence class can handle no evidence.
    """
    evidence = Evidence().no_match()
    assert evidence.exact_context == "None"
    assert evidence.local_context == "No Evidence Found"
    assert evidence.wider_context == "No Evidence Found"

def test_evidence_from_char_startend():
    """
    Tests that the case_extraction.case.Evidence class can handle evidence from a character start and end index.
    """
    evidence = Evidence.from_character_startend("This is a test", 0, 10)
    assert evidence.exact_context == "This is a "
    assert evidence.local_context == "This is a test"
    assert evidence.wider_context == "This is a test"

def test_evidence_from_spacy():
    """
    Tests that the case_extraction.case.Evidence class can handle evidence from a spacy object.
    """
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test")
    evidence = Evidence.from_spacy(doc, 0, 3)
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
    evidence = Evidence.from_spacy_multiple(doc, [("This", 0, 1), ("test", 4, 4)])
    assert evidence.exact_context == "This, test"
    assert evidence.local_context == "This, test"
    assert evidence.wider_context == "This is a test | This is a test"

def test_case_field():
    """
    Tests that the case_extraction.case.CaseField class can handle no evidence.
    """
    from case_extraction.case import CaseField
    field = CaseField(value="test", confidence=0.5, evidence=Evidence.no_match())
    assert field.value == "test"
    assert field.confidence == 0.5
    assert field.evidence.exact_context == "None"
    assert field.evidence.local_context == "No Evidence Found"
    assert field.evidence.wider_context == "No Evidence Found"

def test_case():
    """
    Tests that the case_extraction.case.Case class can handle no evidence.
    """
    from case_extraction.case import Case
    from case_extraction.case import CaseField
    case = Case(filename="test.pdf", method="test")
    case.add_field("test", CaseField(value="test_value", confidence=0.5, evidence=Evidence.no_match()))
    assert case.filename == "test.pdf"
    assert case.method == "test"
    assert case.test.value == "test_value"
    assert case.test.confidence == 0.5
    assert case.test.evidence.exact_context == "None"
    assert str(case) == "No case name extracted"
    case.add_field("defendants", CaseField(value="John Smith", confidence=0.5, evidence=Evidence.no_match()))
    assert str(case) == "R v. John Smith"

def test_case_add_dict():
    """
    Tests that the case_extraction.case.Case add_dict function adds casefields to the case.
    """
    from case_extraction.case import Case
    from case_extraction.case import CaseField
    case = Case(filename="test.pdf", method="test")
    case.add_dict({"test": CaseField(value="test_value", confidence=0.5, evidence=Evidence.no_match())})
    assert case.filename == "test.pdf"
    assert case.method == "test"
    assert case.test.value == "test_value"
    assert case.test.confidence == 0.5
    assert case.test.evidence.exact_context == "None"




