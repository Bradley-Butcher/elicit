from pydantic import main
from case_extraction.utils.example_cases import load_test_cases

from pathlib import Path

from case_extraction.pipelines import main_flow, run_ensemble
from case_extraction.utils.performance import comparison_table

import json 


crown_court_path = Path(__file__).parent.parent / "pdfs" / "crown court"
schema_path = Path(__file__).parent.parent / "schema"

if __name__ == "__main__":
    cases = load_test_cases()[:1]
    filenames = []
    for case in cases:
        filenames.append(crown_court_path / case.filename)
    vector_output = run_ensemble(main_flow, ensemble_args={"mode": "vector"}, pdfs=filenames, question_schema = schema_path / "questions.yml", categories_schema = schema_path / "categories.yml", keyword_schema = schema_path / "keywords.yml")
    with open("sample.json", "w") as outfile:
        json.dump(vector_output, outfile) 
