from pathlib import Path
from typing import Callable, List

import pandas as pd

from case_extraction.case import Case
from case_extraction.pipelines import run_ensemble


def comparison_table(flow: Callable, test_cases: List[Case], ensemble_mode: str, pdf_dir: Path, question_schema: Path, category_schema: Path) -> pd.DataFrame:
    comparisons = {}
    filenames = []
    for case in test_cases:
        filenames.append(pdf_dir / case.filename)
    def _get_case_by_filename(filename: str) -> Case:
        for case in test_cases:
            if filename in case.filename:
                return case
        raise ValueError(f"No case found for {filename}")
    cases = run_ensemble(
        flow, 
        ensemble_mode=ensemble_mode,
        pdfs=filenames,
        question_schema=question_schema,
        categories_schema=category_schema)
    for case_name, case_object in cases.items():
        case = _get_case_by_filename(case_name)
        comparisons = {**comparisons, **case_object.compare(case)}
    return pd.DataFrame.from_dict(comparisons, orient='index')