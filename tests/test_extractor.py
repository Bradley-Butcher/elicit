from pathlib import Path

import pytest

from elicit.extractor import Extractor
from elicit.interface import CategoricalLabellingFunction, Extraction


class ExampleLabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:

        kw_dicts = self.get_schema("keywords", variable_name)
        exts = []
        for k, kws in kw_dicts.items():
            for kw in kws:
                if kw in document_text:
                    exts.append(Extraction(k, kw, kw, kw, 1))
        self.push_many(
            document_name=document_name,
            variable_name=variable_name,
            extraction_list=exts)

    def train(self, document_name: str, variable_name: str, extraction: Extraction):
        pass

    def load(self) -> None:
        self.model = "test_model"

    @property
    def labelling_method(self) -> str:
        return "Test Labelling Function"


@pytest.yield_fixture(scope='session')
def extractor():
    test_db_path = Path(__file__).parent / "test_db.sqlite"
    test_db_path.unlink(missing_ok=True)
    schema_path = Path(__file__).parent / "test_schema"
    document_path = Path(__file__).parent / "test_documents"

    extractor = Extractor(test_db_path)
    extractor.register_schema(
        schema_path / "test_categories.yml", "categories")
    extractor.register_schema(schema_path / "test_keywords.yml", "keywords")
    extractor.register_labelling_function(ExampleLabellingFunction)
    extractor.run(list(document_path.glob("*.txt")))
    yield extractor
    test_db_path.unlink(missing_ok=True)


def test_extractor_registers_schemas(extractor):
    assert "categories" in extractor.schemas
    assert "keywords" in extractor.schemas


def test_extractor_registers_labelling_functions(extractor):
    assert len(extractor.lfs) == 1
    assert extractor.lfs[0].labelling_method == "Test Labelling Function"


def test_database_is_created(extractor):
    assert extractor.logger.db


def test_database_is_populated(extractor):
    assert extractor.logger.db.execute(
        "SELECT COUNT(*) FROM document").fetchone()[0] > 0


def test_all_docs_in_db(extractor):
    docs = [doc.stem for doc in list(
        (Path(__file__).parent / "test_documents").glob("*.txt"))]
    db_docs = extractor.logger.db.execute(
        "SELECT document_name FROM document").fetchall()
    assert set(docs) == set([doc[0] for doc in db_docs])


def test_extractions_are_populated(extractor):
    assert extractor.logger.db.execute(
        "SELECT COUNT(*) FROM extraction").fetchone()[0] == 14


def test_loading(extractor):
    assert extractor.lfs[0].model == "test_model"
