"""Script which tests the vectorizer module."""


def test_output_get_vector():
    """
    Test the get_vector method of the Output class.
    """
    from elicit.vectorizer import Output
    from elicit.document import Extraction
    output = Output(["method1", "method2"], [1, 2], [
                    Extraction.abstain(), Extraction.abstain()])
    assert output.get_vector("method1") == 1
    assert output.get_vector("method2") == 2


def test_output_get_evidence():
    """
    Test the get_evidence method of the Output class.
    """
    from elicit.vectorizer import Output
    from elicit.document import Extraction
    output = Output(["method1", "method2"], [1, 2], [
                    Extraction.abstain(), Extraction.abstain()])
    assert output.get_evidence("method1") == Extraction.abstain()
    assert output.get_evidence("method2") == Extraction.abstain()


def test_vectorizer_match_cases():
    """
    Test the match_cases method of the Vectorizer class.
    """
    from elicit.vectorizer import Vectorizer
    from elicit.document import Document, DocumentField, Extraction
    vectorizer = Vectorizer()
    case_1 = Document(filename="test.pdf", method="test_method")
    case_1.add_field("test", DocumentField(value="test_value",
                     confidence=0.5, evidence=Extraction.abstain()))
    case_2 = Document(filename="test.pdf", method="other_method")
    case_2.add_field("test", DocumentField(value="test_value",
                     confidence=0.5, evidence=Extraction.abstain()))
    cases = [case_1, case_2]
    output = vectorizer.match_cases(cases)
    assert "test.pdf" in output


def test_vectorizer_apply_weighting():
    """
    Test the apply_weighting method of the Vectorizer class.
    """
    from elicit.vectorizer import Vectorizer
    from elicit.document import Document, DocumentField, Extraction
    vectorizer = Vectorizer(flow_weighting={"test_method": 2})
    case_1 = Document(filename="test.pdf", method="test_method")
    case_1.add_field("test", DocumentField(value="test_value",
                     confidence=0.5, evidence=Extraction.abstain()))
    output = vectorizer.apply_weighting([case_1])
    assert output[0].test.confidence == 1.0


def test_vectorizer_identify_methods():
    """
    Test the identify_methods method of the Vectorizer class.
    """
    from elicit.vectorizer import Vectorizer
    from elicit.document import Document, DocumentField, Extraction
    vectorizer = Vectorizer()
    case_1 = Document(filename="test.pdf", method="test_method")
    case_1.add_field("test", DocumentField(value="test_value",
                     confidence=0.5, evidence=Extraction.abstain()))
    case_2 = Document(filename="test.pdf", method="other_method")
    case_2.add_field("test", DocumentField(value="test_value",
                     confidence=0.5, evidence=Extraction.abstain()))
    cases = [case_1, case_2]
    vectorizer.identify_methods(cases)
    assert "test_method" in vectorizer.methods
    assert "other_method" in vectorizer.methods


def test_vectorizer_get_output_value():
    """
    Test the get_output_value method of the Vectorizer class.
    """
    from elicit.vectorizer import Vectorizer
    from elicit.document import Document, DocumentField, Extraction
    vectorizer = Vectorizer()
    case_1 = Document(filename="test.pdf", method="test_method")
    case_1.add_field("test", DocumentField(value="test_value",
                     confidence=0.7, evidence=Extraction.abstain()))
    case_2 = Document(filename="test.pdf", method="other_method")
    case_2.add_field("test", DocumentField(value="test_value",
                     confidence=0.5, evidence=Extraction.abstain()))
    cases = [case_1, case_2]
    vectorizer.identify_methods(cases)
    vectors, evidence, methods = vectorizer.get_output_value(
        cases, "test", "test_value")
    assert set(methods) - {"test_method", "other_method"} == set()
    assert all(e == Extraction.abstain() for e in evidence)
    assert set(vectors) - {0.7, 0.5} == set()


def test_vectorizer_get_value_list():
    """
    Test the get_value_list method of the Vectorizer class.
    """
    from elicit.vectorizer import Vectorizer
    from elicit.document import Document, DocumentField, Extraction
    vectorizer = Vectorizer()
    case_1 = Document(filename="test.pdf", method="test_method")
    case_1.add_field("test", DocumentField(value="test_value",
                     confidence=0.7, evidence=Extraction.abstain()))
    case_2 = Document(filename="test.pdf", method="other_method")
    case_2.add_field("test", DocumentField(value="test_value_2",
                     confidence=0.5, evidence=Extraction.abstain()))
    cases = [case_1, case_2]
    values = vectorizer.get_value_list(cases, "test")
    assert set(values) - {"test_value", "test_value_2"} == set()


def test_vectorize():
    """
    Test the vectorize method of the Vectorizer class.
    """
    from elicit.vectorizer import Vectorizer
    from elicit.document import Document, DocumentField, Extraction
    vectorizer = Vectorizer()
    doc_1 = Document(filename="test.pdf", method="test_method")
    doc_1.add_field("test", DocumentField(value="test_value",
                                          confidence=0.7, evidence=Extraction.abstain()))
    doc_2 = Document(filename="test.pdf", method="other_method")
    doc_2.add_field("test", DocumentField(value="test_value_2",
                                          confidence=0.5, evidence=Extraction.abstain()))
    cases = [doc_1, doc_2]
    vectorizer.identify_methods(cases)
    output = vectorizer.vectorize(cases)
    assert "test" in output
    assert output["test"]["test_value"]["methods"][0] == "other_method"
    assert output["test"]["test_value"]["methods"][1] == "test_method"
    assert output["test"]["test_value"]["vector"][0] == 0
    assert output["test"]["test_value"]["vector"][1] == 0.7
