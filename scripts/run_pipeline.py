"""Script which runs the test cases."""
from pathlib import Path

from elicit.default_extractors import generic_extractor


txt_path = Path(__file__).parent.parent / "data" / "txts"
schema_path = Path(__file__).parent.parent / "schema"
db_path = Path(__file__).parent.parent / "database"

if __name__ == "__main__":
    filenames = [f for f in txt_path.glob("*.txt")][:20]
    generic_extractor(
        docs=filenames,
        db_path=db_path / "test_db.sqlite",
        question_schema=schema_path / "questions.yml",
        categories_schema=schema_path / "categories.yml",
        keyword_schema=schema_path / "keywords.yml",
    )
