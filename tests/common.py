from pathlib import Path
import random
from database.db_utils import build_tables, connect_db, query_db
from elicit.interface import ElicitLogger, Extraction


def database():
    db_path = Path(__file__).parent / "test_db.sqlite"
    db_path.unlink(missing_ok=True)
    sql_path = Path(__file__).parent.parent / "database" / "db_schema.sql"
    n_data = 100
    n_vars = 10
    db = connect_db(db_path)
    build_tables(db, sql_path)
    logger = ElicitLogger(db_path)
    for i in range(n_data):
        for j in range(n_vars):
            val = random.randint(1, 3)
            e = Extraction(f"value_{val}", None, None, None, 1, None, None)
            logger.push(f"doc_{i}", f"var_{j}", e, f"test_{val}")
            selector = random.random()
            if selector > 0.5:
                query_db(
                    db, f"UPDATE extraction SET valid='TRUE' WHERE document_id={i} AND variable_id={(i*n_vars)+j}")
            elif selector < 0.1:
                query_db(
                    db, f"UPDATE extraction SET valid='FALSE' WHERE document_id={i} AND variable_id={(i*n_vars)+j}")
            db.commit()
    return db_path
