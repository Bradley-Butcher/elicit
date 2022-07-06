"""Functions to test the DB utils."""
from venv import create
import pytest
from io import StringIO

import pandas as pd

from user_interface.server.app import create_app
from .common import database


@pytest.yield_fixture(scope="session")
def server():
    db_path = database()
    app = create_app(db_path)
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    with app.test_client() as client:
        yield client
    db_path.unlink(missing_ok=True)


def test_download_data(server):
    with server.get("/api/download_data/", follow_redirects=True) as response:
        data = pd.read_csv(StringIO(response.data.decode("utf-8")))
    assert all(data.columns == ["document_name",
               *[f"var_{i}" for i in range(10)]])
    assert len(data) == 100
