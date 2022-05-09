from pathlib import Path
from typing import List

from elicit.labelling_functions.keyword_search import exact_match as keyword_match
from elicit.labelling_functions.nli_transformer import nli_extraction
from elicit.labelling_functions.similarity_transformer import sim_extraction
from elicit.labelling_functions.semantic_search import search
from elicit.labelling_functions.mask_transformer import mask_extraction

from elicit.pipeline import Pipeline

def core_pipeline(
    docs: List[Path],
    question_schema: Path,
    categories_schema: Path,
    keyword_schema: Path,
    ):
    """
    Core pipeline showing how to use the pipeline.

    :param pdfs: The list of PDFs to process.
    :param question_schema: The question schema.
    :param categories_schema: The categories schema.
    :param keyword_schema: The keyword schema.
    """
    pipeline = Pipeline()

    # Register schemas
    pipeline.register_schema(schema=question_schema, schema_name="question_schema")
    pipeline.register_schema(schema=categories_schema, schema_name="categories_schema")
    pipeline.register_schema(schema=keyword_schema, schema_name="keyword_schema")
    # pipeline.register_schema(schema=mask_schema, schema_name="mask_schema")

    # Register functions
    pipeline.register_function(nli_extraction)
    pipeline.register_function(sim_extraction)
    pipeline.register_function(keyword_match)
    pipeline.register_function(search)
    # pipeline.register_function(mask_extraction)

    # Run pipeline - results are stored in db
    pipeline.run(docs)