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


@app.route('/api/get_data/', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_data():
    vars = query_db(db, "SELECT * FROM variable")
    vars_df = pd.DataFrame(vars)

    def handle_var(doc_group: pd.DataFrame):
        def handle_var_val(val_group: pd.DataFrame):
            select = val_group[val_group["human_response"] == "correct"]
            if len(select) == 0:
                return "N/A"
            else:
                return select["variable_value"].values[0]
        df = doc_group.groupby("variable_name").apply(
            lambda x: handle_var_val(x)).to_frame("variable_value").reset_index().T
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        return df
    docs_df = pd.DataFrame(
        query_db(db, "SELECT document_id, document_name FROM document"))
    df = vars_df.groupby("document_id").apply(lambda x: handle_var(x))
    df = df.merge(docs_df, on="document_id")
    return df.to_csv(index=False)


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


@ app.route('/api/get_response_statuses/<doc_name>', methods=['GET'])
@ cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def response_statuses(doc_name):
    cases = query_db(
        db, f"SELECT * FROM document WHERE document_name='{doc_name}' LIMIT 1")[0]
    variables = query_db(
        db, f"SELECT * FROM variable WHERE document_id={cases['document_id']}")
    results = Counter()
    variable_df = pd.DataFrame(variables)
    for name, group in variable_df.groupby("variable_name"):
        answered = len(group[group["human_response"].notnull()])
        results["partial"] += 1 if answered > 0 else 0
        results["complete"] += 1 if answered == len(group) else 0
        results["total"] += 1
    return jsonify(results)


@ app.route('/api/get_precision/<variable_name>/<binary>', methods=['GET'])
@ cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_precision(variable_name: str, binary: bool):
    # Get Matrix of Variable Value Confidence
    variables = query_db(
        db, f"SELECT * FROM variable WHERE variable_name='{variable_name}'")
    # get first set of extractions where variable id = the first variable id
    extractions = query_db(
        db, f"SELECT * FROM extraction WHERE variable_id={variables[0]['variable_id']}")
    # get all methods from extractions
    methods = {e['method'] for e in extractions}

    df = pd.DataFrame(columns=methods.union({"variable_name", "label"}))

    binary = True if binary == "true" else False

    for variable in variables:
        row = {}
        for extraction in query_db(db, f"SELECT * FROM extraction WHERE variable_id={variable['variable_id']}"):
            try:
                confidence = float(extraction["confidence"])
            except ValueError:
                confidence = 0
            row[extraction["method"]] = confidence
            row["label"] = 1 if variable["human_response"] == "correct" else 0
        row["variable_name"] = variable["variable_name"]
        df = df.append(row, ignore_index=True)
    method_tp = {}
    method_total = {}
    for method in methods:
        if not binary:
            method_tp[method] = df[df["label"] == 1][method].sum()
            method_total[method] = df[method].sum()
        else:
            method_tp[method] = (df[df["label"] == 1][method] > 0).sum()
            method_total[method] = (df[method] > 0).sum()
    precision = {method: method_tp[method] /
                 method_total[method] for method in methods}
    data = {
        "labels": list(precision.keys()),
        "datasets": [
            {
                "label": "Precision",
                "data": [precision[method] for method in methods],
                "backgroundColor": "rgba(54,73,93,.5)",
                "borderColor": "#36495d",
                "borderWidth": 3
            }
        ]
    }
    return jsonify(data)


@ app.route('/api/get_accuracy', methods=['GET'])
@ cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def get_accuracy():
    df = pd.DataFrame(query_db(db, f"SELECT variable.document_id, document.document_name, extraction.confidence as extraction_confidence, variable.confidence as variable_confidence, human_response, variable_name, variable_value FROM extraction LEFT JOIN variable ON extraction.variable_id=variable.variable_id LEFT JOIN document ON variable.document_id=document.document_id"))
    df["extraction_confidence"] = df["extraction_confidence"].astype(float)
    df["variable_confidence"] = df["variable_confidence"].astype(float)
    grouped = df.groupby(["variable_name", "document_name"])

    def get_topk(group, var: str, k: int = 1, threshold: float = 0, operator: str = "sum"):
        g = group.groupby("variable_value").agg({var: operator, "extraction_confidence": "sum"}).sort_values(
            by=var, ascending=False).head(k).reset_index()
        g = g[g["extraction_confidence"] > 0]
        g = g[g[var] > threshold]["variable_value"].tolist()
        if len(g) > 0:
            return g
        else:
            return "abstain"

    def get_human_response(group):
        # if any human response is correct return the variable value
        if any(group["human_response"] == "correct"):
            return group[group["human_response"] == "correct"]["variable_value"].tolist()[0]
        if not any(group["human_response"]):
            return "not complete"
        return "abstain"

    response_df = grouped.apply(get_human_response).to_frame(
        "response").reset_index()
    topk_df = grouped.apply(get_topk, var="extraction_confidence", k=1).to_frame(
        "topk").reset_index()
    lr_df = grouped.apply(get_topk, var="variable_confidence", k=1,
                          threshold=0, operator="first").to_frame("lr").reset_index()

    df = topk_df.merge(response_df, on=["variable_name", "document_name"])
    df = df[df.response != "not complete"]
    df = df[df.topk != "abstain"]
    df["correct"] = df.apply(lambda x: x["response"] in x["topk"], axis=1)

    topk_accuracy = df.groupby("variable_name").apply(
        lambda x: x["correct"].sum() / len(x)).to_frame("topk_accuracy").reset_index()

    df = lr_df.merge(response_df, on=["variable_name", "document_name"])
    df = df[df.response != "not complete"]
    df = df[df.lr != "abstain"]
    df["correct"] = df.apply(lambda x: x["response"] in x["lr"], axis=1)

    lr_accuracy = df.groupby("variable_name").apply(
        lambda x: x["correct"].sum() / len(x)).to_frame("lr_accuracy").reset_index()

    accuracy = topk_accuracy.merge(lr_accuracy, on="variable_name", how="left")
    accuracy = accuracy.fillna(0)

    # convert to list of dicts
    data = {
        "labels": [a.title() for a in accuracy.variable_name],
        "datasets": [
            {
                "label": "Majority Rules",
                "data": accuracy.topk_accuracy.to_list(),
                "backgroundColor": "#00796B",
                "borderColor": "#36495d",
                "borderWidth": 3
            },
            {
                "label": "LR Confidence",
                "data": accuracy.lr_accuracy.to_list(),
                "backgroundColor": "#388E3C",
                "borderColor": "#36495d",
                "borderWidth": 3
            }
        ]
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
