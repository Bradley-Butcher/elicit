import pytest

from database.db_utils import connect_db, query_db
from .common import database

from user_interface.server.sorting import set_confidence, get_data, get_variable_data


@pytest.yield_fixture(scope="session")
def db():
    db_path = database()
    db = connect_db(db_path)
    yield db
    db_path.unlink()


def test_set_confidence(db):
    set_confidence(db, 0, 0.5)
    assert float(query_db(db, "SELECT confidence FROM variable WHERE variable_id=0")[
        0][0]) == 0.5
    set_confidence(db, 0, 0.6)
    assert float(query_db(db, "SELECT confidence FROM variable WHERE variable_id=0")[
        0][0]) == 0.6


def test_get_data(db):
    df = get_data(db, "var_0")
    assert len(df) == 100


def test_get_variable_data(db):
    df = get_data(db, "var_0")
    X, y = get_variable_data(df, training=False)
    assert len(X.columns) == 3
