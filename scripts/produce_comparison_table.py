from case_extraction.utils.example_cases import load_test_cases

from pathlib import Path

from case_extraction.pipelines import main_flow
from case_extraction.utils.performance import comparison_table

crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"
schema_path = Path(__file__).parent.parent / "schema"

if __name__ == "__main__":
    cases = load_test_cases()
    comparison_table(
        main_flow,
        cases,
        "majority",
        crown_court_path, 
        schema_path / "questions.yml", 
        schema_path / "categories.yml"
    ).to_csv("output_table.csv")