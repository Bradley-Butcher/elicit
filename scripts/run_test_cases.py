"""Script which runs the test cases."""
from pathlib import Path

from scripts.example_cases import load_test_cases
from elicit.example_pipelines import demo_pipeline


crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"
schema_path = Path(__file__).parent.parent / "schema"

if __name__ == "__main__":
    cases = load_test_cases()
    filenames = [crown_court_path / case.filename for case in cases]
    demo_pipeline(
        pdfs=filenames, 
        question_schema = schema_path / "demo_questions.yml", 
        categories_schema = schema_path / "demo_categories.yml", 
        keyword_schema = schema_path / "demo_keywords.yml"
    )
