from pathlib import Path
import pytest

from database.db_utils import connect_db, query_db
from elicit.performance import performance
from user_interface.server.sorting import learn_meta_classifier
from .common import database


@pytest.yield_fixture(scope="session")
def db():
    db_path = database()
    db = connect_db(db_path)
    yield db
    db_path.unlink(missing_ok=True)


@pytest.yield_fixture(scope="session")
def db_catdog():
    db_path = Path(__file__).parent / "catdog.sqlite"
    db = connect_db(db_path)
    yield db


def test_agreement(db):
    perf = performance(db, "agreement")
    assert perf["var_0"] < 0.5


def test_confidence(db):
    learn_meta_classifier(db)
    perf = performance(db, "confidence")
    assert perf["var_0"] < 0.5


def test_catdog_confidence(db_catdog):
    perf = performance(db_catdog, "confidence")
    assert perf["cat_or_dog"] == 1


def test_catdog_agreement(db_catdog):
    perf = performance(db_catdog, "agreement")
    assert perf["cat_or_dog"] == 1


def test_catdog_meta_confidence(db_catdog):
    perf = performance(db_catdog, "meta_confidence")
    assert perf["cat_or_dog"] == 1
