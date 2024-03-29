import pytest

from database.db_utils import connect_db, query_db
from .common import database

from user_interface.server.sorting import learn_meta_classifier, set_meta_confidence, get_data, get_variable_data, update_confidence


@pytest.yield_fixture(scope="session")
def db():
    db_path = database()
    db = connect_db(db_path)
    yield db
    db_path.unlink(missing_ok=True)


def test_set_meta_confidence(db):
    set_meta_confidence(db, 0, 0.5)
    assert float(query_db(db, "SELECT meta_confidence FROM extraction WHERE extraction_id=0")[
        0][0]) == 0.5
    set_meta_confidence(db, 0, 0.6)
    assert float(query_db(db, "SELECT meta_confidence FROM extraction WHERE extraction_id=0")[
        0][0]) == 0.6


def test_get_data(db):
    df = get_data(db, "var_0", include_value=False)
    assert df.document_id.nunique() == 100


def test_get_variable_data(db):
    df = get_data(db, "var_0")
    _, X, y = get_variable_data(df[0], training=False)
    assert len(X.columns) == 3


def test_update_confidence(db):
    update_confidence(db)
    learn_meta_classifier(db)
    val_confidences = query_db(db, "SELECT value_confidence FROM variable")
    meta_confidences = query_db(db, "SELECT meta_confidence FROM extraction")
    assert all(c[0] is not None for c in val_confidences)
    assert all(c[0] is not None for c in meta_confidences)
