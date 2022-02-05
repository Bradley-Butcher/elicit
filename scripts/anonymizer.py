from pathlib import Path
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig

from elicit.utils.loading import pdf_to_plaintext
from scripts.example_cases import load_test_cases


crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"



if __name__ == "__main__":
    # Load test cases
    cases = load_test_cases()
    filenames = [crown_court_path / case.filename for case in cases]

    # Register recognizers
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()

    analyzer = AnalyzerEngine(registry=registry)

    text = pdf_to_plaintext(filenames[0])

    result = analyzer.analyze(text=text, language="en")

    engine = AnonymizerEngine()

    output = engine.anonymize(
    text=text,
    analyzer_results=result,
    operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
)

    print(output)