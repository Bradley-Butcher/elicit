"""Script which runs the test cases."""
from pathlib import Path

from elicit.example_pipelines import demo_pipeline


demo_path = Path(__file__).parent.parent / "pdfs" / "crown court"
schema_path = Path(__file__).parent.parent / "schema"

if __name__ == "__main__":
    filenames = [f for f in demo_path.glob("*.pdf")]
    demo_pipeline(
        docs=filenames, 
        question_schema = schema_path / "offense_questions.yml", 
        categories_schema = schema_path / "offense_categories.yml", 
        keyword_schema = schema_path / "offense_keywords.yml",
        mask_schema = schema_path / "offense_masks.yml",
    )
