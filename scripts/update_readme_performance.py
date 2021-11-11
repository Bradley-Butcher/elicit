import pandas as pd
from case_extraction.utils import update_readme

from pathlib import Path

if __name__ == "__main__":
    filepath = Path(__file__).parent.parent / "tests" / \
        "test_case_performance.csv"
    if filepath.exists():
        update_readme(pd.read_csv(filepath))
    else:
        print("No test case performance file found - run tests/test_performance.py regression test")
