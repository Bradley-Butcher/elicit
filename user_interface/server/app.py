from functools import partial
import sqlite3
from typing import List
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from pathlib import Path
import json
from collections import Counter
from numpy import extract
import pandas as pd
import numpy as np

from database.db_utils import connect_db, query_db
from classifier import get_confidence

import argparse

# get db path via argparse
parser = argparse.ArgumentParser()
parser.add_argument("--db_path", type=str,
                    default=Path(__file__).parents[2] / "database" / "test_db.sqlite")
args = parser.parse_args()


db_path = Path(args.db_path) if isinstance(args.db_path, str) else args.db_path
data = json.load(open(Path(__file__).parent / "sample.json"))
db = connect_db(db_path)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


db.row_factory = dict_factory

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/api": {"origins": "*"}})

# sanity check route


@app.route('/api/case_variables/<case_name>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_case_variables(case_name):
    idx = query_db(
        db, f"SELECT * FROM document WHERE document_name='{case_name}' LIMIT 1")[0]["document_id"]
    variables = query_db(db, f"SELECT * FROM variable WHERE document_id={idx}")
    return jsonify(variables)


@app.route('/api/case_evidence/<doc_var_ids>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_case_evidence(doc_var_ids: List[int]):
    evidence = []
    doc_var_ids = doc_var_ids.split(",")
    for doc, var in zip(*(iter(doc_var_ids),) * 2):
        output = query_db(
            db, f"SELECT * FROM extraction WHERE document_id='{doc}' AND variable_id='{var}'")
        evidence += output
    return jsonify(evidence)


@app.route('/api/get_variable_list', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_variable_list():
    output = query_db(db, f"SELECT DISTINCT	variable_name FROM variable")
    return jsonify([v["variable_name"] for v in output])


@app.route('/api/submit_answer/<extraction_id>/<answer>', methods=['POST', 'GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def submit_answer(extraction_id: int, answer: str):
    query_db(db,
             f"UPDATE extraction SET valid='{answer}' WHERE extraction_id={extraction_id}")
    db.commit()
    return "OK"


@app.route('/api/download_data/', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def download_data():
    # get all docs
    docs = query_db(db, "SELECT document_name, document_id FROM document")
    doc_df = pd.DataFrame(docs)

    # Get all variables
    vars = query_db(
        db, "SELECT variable_id, variable_name, variable_value FROM variable")
    vars_df = pd.DataFrame(vars)
    # Get all extractions
    extractions = query_db(db, "SELECT extraction_id, valid FROM extraction")
    extractions_df = pd.DataFrame(extractions)

    # merge
    df = pd.merge(doc_df, vars_df, on="variable_id")
    df = pd.merge(df, extractions_df, on="extraction_id")

    # New Dataframe: each row is a document/variable with a list of validated values
    df = df.groupby(["document_name", "variable_name"]).apply(
        lambda x: [xi["variable_value"] for xi in x if x["valid"] == "TRUE"]).to_frame("validated_vals").reset_index()

    # Pivot out the variables, making each column correspond to a variable, and each row a document.
    df = df.pivot(index="document_name", columns=[
                  "variable_name"], values=["validated_vals"])
    return df.to_csv(index=False)

    # def handle_var(doc_group: pd.DataFrame):
    #     def handle_var_val(val_group: pd.DataFrame):
    #         select = val_group[val_group["human_response"] == "correct"]
    #         if len(select) == 0:
    #             return "N/A"
    #         else:
    #             return select["variable_value"].values[0]
    #     df = doc_group.groupby("variable_name").apply(
    #         lambda x: handle_var_val(x)).to_frame("variable_value").reset_index().T
    #     df.columns = df.iloc[0]
    #     df = df.iloc[1:]
    #     return df
    # docs_df = pd.DataFrame(
    #     query_db(db, "SELECT document_id, document_name FROM document"))
    # df = vars_df.groupby("document_id").apply(lambda x: handle_var(x))
    # df = df.merge(docs_df, on="document_id")
    # return df.to_csv(index=False)


def clean_title(title: str) -> str:
    title = title.replace("_", " ").title()
    title = title.replace("-", "").replace(" V ", " v ")
    return title[:30] + "..." if len(title) > 30 else title


@app.route('/api/update_confidence/', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def update_confidence():
    variables = query_db(db, "SELECT * FROM variable")
    extractions = query_db(db, f"SELECT * FROM extraction")
    indicies, confidences = get_confidence(variables, extractions)
    for idx, confidence in zip(indicies, confidences):
        query_db(
            db, f"UPDATE variable SET confidence={'NULL' if confidence == '?' else confidence} WHERE variable_id={idx}")
    db.commit()
    return "OK"


@app.route('/api/get_cases', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_case_names():
    cases = query_db(db, f"SELECT * FROM document")
    cases = [c["document_name"] for c in cases]
    menu = []
    for case in cases:
        menu.append({
            "title": clean_title(case),
            "case_id": case,
        })
    response = jsonify(menu)
    return response


@app.route('/api/get_document_status', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_document_statuses():
    documents = query_db(db, f"SELECT * FROM document")
    variables = query_db(db, f"SELECT * FROM variable")
    extractions = query_db(db, f"SELECT * FROM extraction")
    variable_df = pd.DataFrame(variables).merge(
        pd.DataFrame(documents), on="document_id")
    df = variable_df.merge(
        pd.DataFrame(extractions), on=["document_id", "variable_id"])
    result = df.groupby(["variable_name", "document_name"]).apply(
        lambda x: any(x["valid"] == "TRUE")).to_frame("variable_complete").reset_index()
    result = result.pivot(index="document_name", columns="variable_name",
                          values="variable_complete").reset_index()
    return jsonify(result.to_json(orient="records"))


if __name__ == '__main__':
    app.run(debug=True)
