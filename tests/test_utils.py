from pathlib import Path
from elicit.generic_labelling_functions.qa_transformer import split_context
from elicit.utils.loading import load_document


def test_split_context():
    document = load_document(Path("data/txts/90.txt"))
    splits = split_context(document)
