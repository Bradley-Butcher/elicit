"""Script containing various utility functions for the database."""
import sqlite3
from pathlib import Path
import json
from typing import List

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


def doc_in_table(db, doc_name: str) -> bool:
    """
    Check if a document is in the database.

    :param db: Connection to the database.
    :param doc_name: Name of the document.

    :return: True if the document is in the database, False otherwise.
    """
    query = f"SELECT document_id FROM document WHERE document_name = '{doc_name}' LIMIT 1"
    return True if query_db(db, query) else False


def get_variables_for_doc(db, doc_id: int, values: List[str]) -> list:
    """
    Get the variables for a document.

    :param db: Connection to the database.
    :param doc_id: ID of the document.

    :return: List of variables for the document.
    """
    query = f"SELECT {', '.join(values)} FROM variable WHERE document_id = {doc_id}"
    return query_db(db, query)


def delete_doc(db, doc_name: str, delete_if_human_response: bool = False) -> None:
    """
    Delete a document from the database.

    :param db: Connection to the database.
    :param doc_name: Name of the document.
    :param delete_if_human_response: Whether to delete the document if it is a human response.

    :return: None
    """
    if delete_if_human_response:
        query = f"DELETE FROM document WHERE document_name = '{doc_name}'"
        db.execute(query)
    doc_id = get_doc_id(db, doc_name)
    variables = get_variables_for_doc(
        db, doc_id, ["variable_id", "human_response"])
    deleted_vars = 0
    for var in variables:
        var_id, human_response = var
        if not human_response:
            query = f"DELETE FROM variable WHERE variable_id = '{var_id}'"
            db.execute(query)
            deleted_vars += 1
    if len(variables) == deleted_vars:
        query = f"DELETE FROM document WHERE document_id = '{doc_id}'"
        db.execute(query)
    db.commit()


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


def variable_in_table(db, var_name: str, variable_value: str, document_id: int) -> bool:
    """
    Check if a variable is in the database.

    :param db: Connection to the database.
    :param var_name: Name of the variable.

    :return: True if the variable is in the database, False otherwise.
    """
    query = f"SELECT variable_id FROM variable WHERE variable_name = '{var_name}' AND variable_value = '{variable_value}' AND document_id = {document_id} LIMIT 1"
    return True if query_db(db, query) else False


def insert_new_doc(db, doc_name: str, doc_dict: dict) -> None:
    values = list(doc_dict.keys())
    next_doc_id = get_next_id(db, 'document')
    document_query = f"INSERT INTO document (document_id, document_name) VALUES ({next_doc_id}, '{doc_name}')"
    try:
        db.execute(document_query)
    except sqlite3.IntegrityError:
        next_doc_id = get_doc_id(db, doc_name)
    # Insert Variables
    for var in values:
        # check if variable_name is in the database for this document
        for val in doc_dict[var].keys():
            if variable_in_table(db, var, val, next_doc_id):
                continue
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
                        print(
                            "Database error. Duplicate case? Use update method to update existing cases.")


def insert_doc_from_dict(db, doc_name: str, doc_dict: dict, delete_if_human_response: bool = False) -> None:
    """
    Insert a doc from a dictionary.

    :param db: Connection to the database.
    :param doc_name: Name of the document.
    :param doc_dict: Dictionary containing the extracted elements from the document to add to the DB.

    :return: None
    """
    # Insert Document
    if doc_in_table(db, doc_name):
        delete_doc(
            db, doc_name, delete_if_human_response=delete_if_human_response)
    insert_new_doc(db, doc_name, doc_dict)


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
