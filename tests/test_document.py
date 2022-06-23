"""Script to test the case module."""
from elicit.document import Extraction


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


def test_case_field():
    """
    Tests that the case_extraction.case.CaseField class can handle no evidence.
    """
    from elicit.document import DocumentField
    field = DocumentField(value="test", confidence=0.5,
                          evidence=Extraction.abstain())
    assert field.value == "test"
    assert field.confidence == 0.5
    assert field.evidence.exact_context == "ABSTAIN"
    assert field.evidence.local_context == None
    assert field.evidence.wider_context == None


def test_case():
    """
    Tests that the Document class can handle no evidence.
    """
    from elicit.document import Document
    from elicit.document import DocumentField
    doc = Document(filename="test.pdf", method="test")
    doc.add_field("test", DocumentField(value="test_value",
                                        confidence=0.5, evidence=Extraction.abstain()))
    assert doc.filename == "test.pdf"
    assert doc.method == "test"
    assert doc.test.value == "test_value"
    assert doc.test.confidence == 0.5
    assert doc.test.evidence.exact_context == "ABSTAIN"


def test_case_add_dict():
    """
    Tests that the case_extraction.case.Case add_dict function adds casefields to the case.
    """
    from elicit.document import Document
    from elicit.document import DocumentField
    case = Document(filename="test.pdf", method="test")
    case.add_dict({"test": DocumentField(value="test_value",
                  confidence=0.5, evidence=Extraction.abstain())})
    assert case.filename == "test.pdf"
    assert case.method == "test"
    assert case.test.value == "test_value"
    assert case.test.confidence == 0.5
    assert case.test.evidence.exact_context == "ABSTAIN"
