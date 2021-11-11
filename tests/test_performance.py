from pathlib import Path
from typing import List, Union
import warnings
import pytest

from case_extraction.example_cases import load_test_cases

from case_extraction.case import Case, comparison_table, performance_table

import pandas as pd
from tqdm import tqdm

test_path = Path(__file__).parent
crown_court_path = test_path.parent / "pdfs" / "crown court"


def test_performance_regression():
    test_cases = load_test_cases()
    new_performance = performance_table(test_cases, crown_court_path)
    if (test_path / "test_case_performance.csv").is_file():
        old_performance = pd.read_csv(
            test_path / "test_case_performance.csv")
        assert all(new_performance.iloc[:, 0] >= old_performance.iloc[:, 0])
    new_performance.to_csv(
        test_path / "test_case_performance.csv")
