from pathlib import Path
import pytest

from elicit.interface import ElicitLogger

from .common import database


@pytest.yield_fixture(scope='session')
def logger() -> ElicitLogger:
    test_db_path = database()
    logger = ElicitLogger(test_db_path)
    yield logger
    test_db_path.unlink(missing_ok=True)


def test_get_validated_document_names(logger: ElicitLogger):
    doc_names = logger.get_validated_document_names("var_0", False)
    count = logger.db.execute(
        """
            SELECT COUNT(*) FROM extraction
            LEFT JOIN variable
            ON extraction.variable_id = variable.variable_id 
            WHERE valid='TRUE' AND variable_name='var_0'
        """
    ).fetchone()[0]
    assert len(doc_names) == count


def test_get_validated_extractions(logger: ElicitLogger):
    doc_names = logger.get_validated_document_names("var_0", False)
    extractions = logger.get_validated_extractions(doc_names, "var_0", False)
    assert len(extractions) == len(doc_names)


def test_get_validated_document_names_negative(logger: ElicitLogger):
    doc_names = logger.get_validated_document_names("var_0", False)
    doc_names_neg = logger.get_validated_document_names("var_0", True)
    assert len(doc_names) < len(doc_names_neg)


def test_get_validated_extractions_negative(logger: ElicitLogger):
    doc_names = logger.get_validated_document_names("var_0", False)
    extractions = logger.get_validated_extractions(doc_names, "var_0", False)
    doc_names_neg = logger.get_validated_document_names("var_0", True)
    extractions_neg = logger.get_validated_extractions(
        doc_names_neg, "var_0", True)
    assert len(extractions) < len(extractions_neg)
    assert any([extraction.valid == "FALSE" for extraction in extractions_neg])
