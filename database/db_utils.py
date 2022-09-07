"""Script containing various utility functions for the database."""
import sqlite3
from pathlib import Path
import json
from typing import List

db_path = Path(__file__).parent / "db.sqlite"
schema_path = Path(__file__).parent / "db_schema.sql"


def get_variables(db):
    variables = query_db(
        db, f"SELECT DISTINCT variable_name FROM variable")
    return [v[0] for v in variables]


def connect_db(db_path: Path = db_path) -> sqlite3.Connection:
    """
    Connect to the database. Build the tables if they don't exist.

    :param db_path: Path to the database.

    :return: Connection to the database.
    """
    if not db_path.exists():
        db = sqlite3.connect(db_path, check_same_thread=False)
        build_tables(db, schema_path)
        return db
    return sqlite3.connect(db_path, check_same_thread=False)


def query_db(db, query, args=(), one=False) -> list:
    """
    Query the database.

    :param db: Connection to the database.
    :param query: Query to execute.
    :param args: Arguments to pass to the query.
    :param one: Whether to return a single value or a list.

    :return: List of results.
    """
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def build_tables(db, sql_file: Path) -> None:
    """
    Build the tables.

    :param db: Connection to the database.
    :param sql_file: Path to the SQL file.

    :return: None
    """
    # if table_exists(db, 'document'):
    #     print("Tables already created.")
    with open(sql_file, 'r') as f:
        db.executescript(f.read())
        db.commit()


def get_next_id(db, table: str) -> int:
    """
    Get the next ID.

    :param db: Connection to the database.
    :param table: Table to get the next ID for.

    :return: Next ID for the table.
    """
    query = f"SELECT MAX({table}_id) FROM {table} LIMIT 1"
    val = query_db(db, query)[0][0]
    return val + 1 if val is not None else 0


def get_doc_id(db, doc_name: str) -> int:
    """
    Get the ID of a document.

    :param db: Connection to the database.
    :param doc_name: Name of the document.

    :return: ID of the document.
    """
    query = f"SELECT document_id FROM document WHERE document_name = '{doc_name}' LIMIT 1"
    try:
        return int(query_db(db, query)[0][0])
    except IndexError:
        return -1


def get_variable_id(db, var_name: str, variable_value: str, document_id: int) -> int:
    """
    Get the ID of a variable.

    :param db: Connection to the database.
    :param var_name: Name of the variable.
    :param variable_value: Value of the variable.
    :param document_id: ID of the document.

    :return: ID of the variable.
    """
    query = f"SELECT variable_id FROM variable WHERE variable_name = '{var_name}' AND variable_value = '{variable_value}' AND document_id = '{document_id}' LIMIT 1"
    try:
        return int(query_db(db, query)[0][0])
    except IndexError:
        return -1


def get_extraction_id(db, extraction_method: str, var_id: int, document_id: int) -> int:
    """
    Get the ID of an extraction.

    :param db: Connection to the database.
    :param extraction_method: Name of the extraction method.
    :param var_name: Name of the variable.
    :param variable_value: Value of the variable.
    :param document_id: ID of the document.

    :return: ID of the extraction.
    """
    query = f"SELECT extraction_id FROM extraction WHERE method = '{extraction_method}' AND variable_id = '{var_id}' AND document_id = '{document_id}' LIMIT 1"
    try:
        return int(query_db(db, query)[0][0])
    except IndexError:
        return -1
