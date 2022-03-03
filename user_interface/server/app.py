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

db_path = Path(__file__).parents[2] / "database" / "db.sqlite"
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
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_case_variables(case_name):
    idx = query_db(db, f"SELECT * FROM document WHERE document_name='{case_name}' LIMIT 1")[0]["document_id"]
    variables = query_db(db, f"SELECT * FROM variable WHERE document_id={idx}")
    return jsonify(variables)

@app.route('/api/case_evidence/<doc_var_ids>', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_case_evidence(doc_var_ids: List[int]):
    evidence = []
    doc_var_ids = doc_var_ids.split(",")
    for doc, var in zip(*(iter(doc_var_ids),) * 2):
        output = query_db(db, f"SELECT * FROM extraction WHERE document_id='{doc}' AND variable_id='{var}'")
        evidence += output
    return jsonify(evidence)

@app.route('/api/get_variable_list', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_variable_list():
    output = query_db(db, f"SELECT DISTINCT	variable_name FROM variable")
    return jsonify([v["variable_name"] for v in output])


@app.route('/api/submit_answer/<variable_id>/<answer>', methods=['POST', 'GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def submit_answer(variable_id: int, answer: str):
    query_db(db, f"UPDATE variable SET human_response='{answer}' WHERE variable_id={variable_id}")
    db.commit()
    return "OK"

@app.route('/api/get_data/', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
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
        df = doc_group.groupby("variable_name").apply(lambda x: handle_var_val(x)).to_frame("variable_value").reset_index().T
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        return df
    docs_df = pd.DataFrame(query_db(db, "SELECT document_id, document_name FROM document"))
    df = vars_df.groupby("document_id").apply(lambda x: handle_var(x))
    df = df.merge(docs_df, on="document_id")
    return df.to_csv(index=False)

def clean_title(title: str) -> str:
    title = title.replace("_", " ").title()
    title = title.replace("-", "").replace(" V ", " v ")
    return title[:30] + "..." if len(title) > 30 else title

@app.route('/api/update_confidence/', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def update_confidence():
    variables = query_db(db, "SELECT * FROM variable")
    extractions = query_db(db, f"SELECT * FROM extraction")
    indicies, confidences = get_confidence(variables, extractions)
    for idx, confidence in zip(indicies, confidences):
        query_db(db, f"UPDATE variable SET confidence={'NULL' if confidence == '?' else confidence} WHERE variable_id={idx}")
    db.commit()
    return "OK"

@app.route('/api/get_cases', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
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
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_document_statuses():
    documents = query_db(db, f"SELECT * FROM document")
    variables = query_db(db, f"SELECT * FROM variable")
    variable_df = pd.DataFrame(variables).merge(pd.DataFrame(documents), on="document_id")
    result = variable_df.groupby(["variable_name", "document_name"]).apply(lambda x: any(x["human_response"] == "correct")).to_frame("variable_complete").reset_index()
    result = result.pivot(index="document_name", columns="variable_name", values="variable_complete").reset_index()
    return jsonify(result.to_json(orient="records"))

@app.route('/api/get_response_statuses/<doc_name>', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def response_statuses(doc_name):
    cases = query_db(db, f"SELECT * FROM document WHERE document_name='{doc_name}' LIMIT 1")[0]
    variables = query_db(db, f"SELECT * FROM variable WHERE document_id={cases['document_id']}")
    results = Counter()
    variable_df = pd.DataFrame(variables)
    for name, group in variable_df.groupby("variable_name"):
        answered = len(group[group["human_response"].notnull()])
        results["partial"] += 1 if answered > 0 else 0
        results["complete"] += 1 if answered == len(group) else 0
        results["total"] += 1
    return jsonify(results)

@app.route('/api/get_precision/<variable_name>/<binary>', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_precision(variable_name: str, binary: bool):
    # Get Matrix of Variable Value Confidence
    variables = query_db(db, f"SELECT * FROM variable WHERE variable_name='{variable_name}'")
    # get first set of extractions where variable id = the first variable id
    extractions = query_db(db, f"SELECT * FROM extraction WHERE variable_id={variables[0]['variable_id']}")
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
    precision = {method: method_tp[method] / method_total[method] for method in methods}
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


@app.route('/api/get_accuracy', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_accuracy():
    variable_df = pd.DataFrame(query_db(db, f"SELECT * FROM variable"))
    grouped = variable_df.groupby(["variable_name", "document_id"])
    def get_total_confidence(row):
        extractions = query_db(db, f"SELECT * FROM extraction WHERE variable_id={row['variable_id']}")
        return sum([float(e["confidence"]) for e in extractions])
    def max_conf(group, majority_vote):
        # if any have human response correct
        if not any(group["human_response"] == "correct"):
            return 0
        if majority_vote:
            # get row with max total confidence
            max_row = group.apply(get_total_confidence, axis=1).idxmax()
            return 1 if group.loc[max_row]["human_response"] == "correct" else 0
        else:
            # get row with max total confidence
            max_val = group.confidence.astype(float).max()
            return 1 if group[group["human_response"] == "correct"].confidence.astype(float).max() == max_val else 0

    maj_results = grouped.apply(partial(max_conf, majority_vote=True)).to_frame("correct").reset_index()
    maj_accuracy = maj_results.groupby("variable_name").correct.sum() / maj_results.groupby("variable_name").correct.size()
    conf_results = grouped.apply(partial(max_conf, majority_vote=False)).to_frame("correct").reset_index()
    conf_accuracy = conf_results.groupby("variable_name").correct.sum() / conf_results.groupby("variable_name").correct.size()

    # convert to list of dicts
    data = {
        "labels": [a.title() for a in maj_accuracy.index],
        "datasets": [
            {
                "label": "Majority Rules",
                "data": [maj_accuracy[variable] for variable in maj_accuracy.index],
                "backgroundColor": "#00796B",
                "borderColor": "#36495d",
                "borderWidth": 3
            },
            {
                "label": "LR Confidence",
                "data": [conf_accuracy[variable] for variable in conf_accuracy.index],
                "backgroundColor": "#388E3C",
                "borderColor": "#36495d",
                "borderWidth": 3
            }
            ]
    }
    return jsonify(data)










if __name__ == '__main__':
    app.run(debug=True)