"""Script which runs the test cases."""
from pathlib import Path

from elicit.example_pipelines import core_pipeline


txt_path = Path(__file__).parent.parent / "data" / "txts"
schema_path = Path(__file__).parent.parent / "schema"

if __name__ == "__main__":
    filenames = [f for f in txt_path.glob("*.txt")]
    core_pipeline(
        docs=filenames, 
        question_schema = schema_path / "questions.yml", 
        categories_schema = schema_path / "categories.yml", 
        keyword_schema = schema_path / "keywords.yml",
    )
