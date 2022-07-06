import pytest

from database.db_utils import connect_db, query_db
from .common import database

from user_interface.server.sorting import set_confidence


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
