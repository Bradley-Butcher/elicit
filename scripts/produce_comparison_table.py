from case_extraction.case import comparison_table, debug_table
from case_extraction.example_cases import load_test_cases

from pathlib import Path

crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"

if __name__ == "__main__":
    cases = load_test_cases()
    comparison_table(cases, crown_court_path).to_csv("output_table.csv")
    # debug_table(cases, crown_court_path).to_csv("debug_table.csv")
