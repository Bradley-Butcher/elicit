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


def update_readme(df: pd.DataFrame) -> None:
    readme = test_path.parent / "README.md"
    with open(readme, "r") as f:
        lines = f.readlines()
    performance_line = 0
    for i, line in enumerate(lines):
        if line.startswith("## Current Performance"):
            performance_line = i + 1
            break
    new_md = df.to_markdown().split("\n")
    lines[performance_line: performance_line + len(new_md)] = new_md
    with open(readme, "w") as f:
        f.write("\n".join([l.replace("\n", "") for l in lines]))


def test_performance_regression():
    test_cases = load_test_cases()
    new_performance = performance_table(test_cases, crown_court_path)
    if (test_path / "test_case_performance.csv").is_file():
        old_performance = pd.read_csv(
            test_path / "test_case_performance.csv")
        assert all(new_performance.iloc[:, 1:] >= old_performance.iloc[:, 1:])
    new_performance.to_csv(
        test_path / "test_case_performance.csv", index=False)
    update_readme(new_performance)


def test_update_readme():
    performance_df = pd.read_csv(
        test_path / "test_case_performance.csv", index_col=0)
    update_readme(performance_df)
