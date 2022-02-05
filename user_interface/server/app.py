import sqlite3
from typing import List
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from pathlib import Path
import json
from collections import Counter
import pandas as pd

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
    df = vars_df.groupby("document_id").apply(lambda x: handle_var(x))
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

@app.route('/api/get_cases/<page>', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization', 'Access-Control-Allow-Origin'])
def get_case_names(page, per_page=300):
    cases = query_db(db, f"SELECT * FROM document LIMIT {per_page} OFFSET {(int(page)-1)*per_page}")
    cases = [c["document_name"] for c in cases]
    menu = []
    for case in cases:
        menu.append({
            "title": clean_title(case),
            "case_id": case,
    })
    response = jsonify(menu)
    return response

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




if __name__ == '__main__':
    app.run(debug=True)