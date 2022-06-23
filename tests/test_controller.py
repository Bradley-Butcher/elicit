from pathlib import Path

import pytest

from elicit.controller import Controller
from elicit.interface import CategoricalLabellingFunction, Extraction


class TestLabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        extraction = document_text.split(".")[0].lower()
        self.logger.push(
            document_name=document_name,
            variable_name=variable_name,
            extraction=Extraction(extraction, extraction,
                                  extraction, extraction, 1),
            method=self.labelling_method)

    def train(self, document_name: str, variable_name: str, extraction: Extraction):
        pass

    @property
    def labelling_method(self) -> str:
        return "Test Labelling Function"


@pytest.yield_fixture(scope='session')
def controller():
    test_db_path = Path(__file__).parent / "test_db.sqlite"
    schema_path = Path(__file__).parent / "test_schema"
    document_path = Path(__file__).parent / "test_documents"

    controller = Controller(test_db_path)
    controller.register_schema(
        schema_path / "test_categories.yml", "categories")
    controller.register_schema(schema_path / "test_keywords.yml", "keywords")
    controller.register_labelling_function(TestLabellingFunction)
    controller.run(list(document_path.glob("*.txt")))
    yield controller
    test_db_path.unlink()


def test_controller_registers_schemas(controller):
    assert "categories" in controller.schemas
    assert "keywords" in controller.schemas


def test_controller_registers_labelling_functions(controller):
    assert len(controller.lfs) == 1
    assert controller.lfs[0].labelling_method == "Test Labelling Function"


def test_database_is_created(controller):
    assert controller.logger.db


def test_database_is_populated(controller):
    assert controller.logger.db.execute(
        "SELECT COUNT(*) FROM document").fetchone()[0] == 1


def test_all_docs_in_db(controller):
    docs = [doc.stem for doc in list(
        (Path(__file__).parent / "test_documents").glob("*.txt"))]
    db_docs = controller.logger.db.execute(
        "SELECT document_name FROM document").fetchall()
    assert set(docs) == set([doc[0] for doc in db_docs])
