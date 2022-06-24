"""Script which runs the test cases."""
from pathlib import Path

from elicit.example_extractor import generic_extractor


txt_path = Path(__file__).parent.parent / "data" / "lawpages_annotated"
schema_path = Path(__file__).parent.parent / "schema"
db_path = Path(__file__).parent.parent / "database"

if __name__ == "__main__":
    filenames = [f for f in txt_path.glob("*.txt")][:3]
    generic_extractor(
        docs=filenames,
        db_path=db_path / "test_db.sqlite",
        question_schema=schema_path / "lawpage_questions.yml",
        categories_schema=schema_path / "lawpage_categories.yml",
        keyword_schema=schema_path / "lawpage_keywords.yml",
    )
