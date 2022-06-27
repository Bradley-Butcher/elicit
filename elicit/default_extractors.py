import imp
from pathlib import Path
from typing import List

from elicit.generic_labelling_functions import *
from elicit.extractor import Extractor


def generic_extractor(
    docs: List[Path],
    db_path: Path,
    question_schema: Path,
    categories_schema: Path,
    keyword_schema: Path,
):
    """
    Generic extractor which runs the generic labelling functions.

    :param docs: List of paths to documents.
    :param db_path: Path to database.
    :param question_schema: Path to question schema.
    :param categories_schema: Path to categories schema.
    :param keyword_schema: Path to keyword schema.
    """
    extractor = Extractor(db_path=db_path)

    # Register schemas
    extractor.register_schema(schema=question_schema,
                              schema_name="questions")
    extractor.register_schema(schema=categories_schema,
                              schema_name="categories")
    extractor.register_schema(schema=keyword_schema,
                              schema_name="keywords")

    # Register functions

    extractor.register_labelling_function(SemanticSearchLF)
    extractor.register_labelling_function(SimilarityLabellingFunction)
    extractor.register_labelling_function(KeywordMatchLF)
    extractor.register_labelling_function(NLILabellingFunction)

    # Run pipeline - results are stored in db
    extractor.run(docs)
