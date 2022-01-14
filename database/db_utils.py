"""Script containing various utility functions for the database."""
import sqlite3
from pathlib import Path
import json

db_path = Path(__file__).parent / "db.sqlite"
schema_path = Path(__file__).parent / "db_schema.sql"

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

def insert_doc_from_dict(db, doc_name: str, doc_dict: dict) -> None:
    """
    Insert a doc from a dictionary.

    :param db: Connection to the database.
    :param doc_name: Name of the document.
    :param doc_dict: Dictionary containing the extracted elements from the document to add to the DB.

    :return: None
    """
    values = list(doc_dict.keys())
    #Insert Document
    next_doc_id = get_next_id(db, 'document')
    document_query = f"INSERT INTO document (document_id, document_name) VALUES ({next_doc_id}, '{doc_name}')"
    db.execute(document_query)
    #Insert Variables
    for var in values:
        for val in doc_dict[var].keys():
            next_var_id = get_next_id(db, 'variable')
            var_query = f"INSERT INTO variable (variable_id, variable_name, variable_value, document_id) VALUES ({next_var_id}, '{var}', '{val}', {next_doc_id})"
            db.execute(var_query)
            # Insert Extraction
            for i in range(len(doc_dict[var][val]["methods"])):
                next_extraction_id = get_next_id(db, 'extraction')
                context = doc_dict[var][val]['evidence'][i]
                if context:
                    extraction_query = f"INSERT INTO extraction (extraction_id, method, confidence, exact_context, local_context, wider_context, document_id, variable_id) VALUES ({next_extraction_id}, '{doc_dict[var][val]['methods'][i]}', '{doc_dict[var][val]['vector'][i]}', '{doc_dict[var][val]['evidence'][i]['exact_context']}', '{doc_dict[var][val]['evidence'][i]['local_context']}', '{doc_dict[var][val]['evidence'][i]['wider_context']}', {next_doc_id}, {next_var_id})"
                    try:
                        db.execute(extraction_query)
                    except:
                        print("Database error. Duplicate case? Use update method to update existing cases.")
                    

def insert_documents_from_json(db, json_file: Path) -> None:
    """
    Insert documents from a JSON file.

    :param db: Connection to the database.
    :param json_file: Path to the JSON file.

    :return: None
    """
    with open(json_file, 'r') as f:
        docs = json.load(f)
    for doc in docs:
        insert_doc_from_dict(db, doc, docs[doc])