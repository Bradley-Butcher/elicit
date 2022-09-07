from pathlib import Path
import random
from database.db_utils import build_tables, connect_db, query_db
from elicit.interface import ElicitLogger, Extraction


def database():
    db_path = Path(__file__).parent / "test_db.sqlite"
    db_path.unlink(missing_ok=True)
    sql_path = Path(__file__).parent.parent / "database" / "db_schema.sql"
    n_data = 100
    n_vars = 2
    db = connect_db(db_path)
    build_tables(db, sql_path)
    logger = ElicitLogger(db_path)
    for i in range(n_data):
        for j in range(n_vars):
            val = random.randint(1, 3)
            methods = random.choices(["method_1", "method_2", "method_3"], k=2)
            valid = random.choices(['TRUE', 'FALSE', None], k=3)
            e1 = Extraction(f"value_{val}", "test",
                            "test", None, random.random(), valid[0], None)
            logger.push(f"doc_{i}", f"var_{j}", e1, methods[0])
            e2 = Extraction(f"value_{val}", "test",
                            "test", None, random.random(), valid[1], None)
            logger.push(f"doc_{i}", f"var_{j}", e2, methods[1])
            val = random.randint(1, 3)
            e3 = Extraction(f"value_{val}", "abc",
                            "abc", None, random.random(), valid[2], None)
            method = random.choice(["method_1", "method_2", "method_3"])
            logger.push(f"doc_{i}", f"var_{j}", e3, method)

            db.commit()
    return db_path
