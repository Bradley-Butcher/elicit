"""Functions to test the DB utils."""
from pathlib import Path
from venv import create
import pytest
import random
from io import StringIO

import pandas as pd

from database.db_utils import connect_db, build_tables, query_db
from elicit.interface import ElicitLogger, Extraction
from user_interface.server.app import create_app


def database():
    db_path = Path(__file__).parent / "test_db.sqlite"
    sql_path = Path(__file__).parent.parent / "database" / "db_schema.sql"
    n_data = 100
    n_vars = 10
    db = connect_db(db_path)
    build_tables(db, sql_path)
    logger = ElicitLogger(db_path)
    for i in range(n_data):
        for j in range(n_vars):
            val = random.randint(1, 3)
            e = Extraction(f"value_{val}", None, None, None, 1)
            logger.push(f"doc_{i}", f"var_{j}", e, "test")
            if random.random() > 0.5:
                query_db(
                    db, f"UPDATE extraction SET valid='TRUE' WHERE document_id={i} AND variable_id={(i*n_vars)+j}")
                db.commit()
    return db_path


@pytest.yield_fixture(scope="session")
def server():
    db_path = database()
    app = create_app(db_path)
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.test_client() as client:
        yield client
    db_path.unlink()


def test_download_data(server):
    with server.get("/api/download_data/", follow_redirects=True) as response:
        data = pd.read_csv(StringIO(response.data.decode("utf-8")))
    assert all(data.columns == ["document_name",
               *[f"var_{i}" for i in range(10)]])
    assert len(data) == 100
