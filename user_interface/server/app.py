from typing import List
from flask import Flask, jsonify, current_app, g
from flask_cors import CORS, cross_origin
from pathlib import Path
import pandas as pd

from database.db_utils import connect_db, query_db
from user_interface.server.sorting import update_confidence

import click


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db():
    if 'db' not in g:
        g.db = connect_db(current_app.config['DATABASE'])
        g.db.row_factory = dict_factory
    return g.db


def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()


def clean_title(title: str) -> str:
    title = title.replace("_", " ").title()
    title = title.replace("-", "").replace(" V ", " v ")
    return title[:30] + "..." if len(title) > 30 else title


def create_app(db_path: Path, test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=db_path)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.config['CORS_HEADERS'] = 'Content-Type'
    cors = CORS(app, resources={r"/api": {"origins": "*"}})

    @app.route('/api/case_variables/<case_name>', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def get_case_variables(case_name):
        db = get_db()
        idx = query_db(
            db, f"SELECT * FROM document WHERE document_name='{case_name}' LIMIT 1")[0]["document_id"]
        variables = query_db(
            db, f"SELECT * FROM variable WHERE document_id={idx}")
        return jsonify(variables)

    @app.route('/api/case_evidence/<doc_var_ids>', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def get_case_evidence(doc_var_ids: List[int]):
        db = get_db()
        evidence = []
        doc_var_ids = doc_var_ids.split(",")
        for doc, var in zip(*(iter(doc_var_ids),) * 2):
            output = query_db(
                db, f"SELECT * FROM extraction WHERE document_id='{doc}' AND variable_id='{var}'")
            evidence += output
        return jsonify(evidence)

    @app.route('/api/document_extractions/<document_name>/<variable_name>', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def document_extractions(document_name: int, variable_name: str):
        db = get_db()
        extractions = {}
        output = query_db(
            db, f"""
            SELECT extraction.extraction_id as extraction_id, extraction.meta_confidence AS meta_confidence,
            extraction.exact_context AS exact_context, extraction.local_context AS local_context,
            extraction.wider_context AS wider_context, extraction.valid AS valid,
            extraction.alert AS alert, variable.variable_name AS variable_name,
            variable.variable_value AS variable_value, variable.value_confidence AS confidence
            FROM extraction AS extraction
            LEFT JOIN variable AS variable
            ON extraction.variable_id = variable.variable_id
            LEFT JOIN document AS document
            ON extraction.document_id = document.document_id
            WHERE document.document_name='{document_name}'
            AND variable.variable_name='{variable_name}'"""
        )

        unique_lfs = len(
            query_db(db, f"SELECT DISTINCT method FROM raw_extraction"))

        def agreement(values):
            def _count(v):
                return len([x for x in v if x["lf"] != "manual"])
            return f"{max([_count(v['lfs']) for v in values])}/{unique_lfs - 1}"

        def get_raw_extractions(extraction_id) -> list:
            return query_db(
                db, f"SELECT method as lf, confidence as lf_confidence FROM raw_extraction WHERE extraction_id={extraction_id}")

        for row in output:
            extraction = {
                "extraction_id": row["extraction_id"],
                "meta_confidence": row["meta_confidence"],
                "exact_context": row["exact_context"],
                "local_context": row["local_context"],
                "wider_context": row["wider_context"],
                "valid": row["valid"],
                "alert": row["alert"],
            }
            extraction["lfs"] = get_raw_extractions(row["extraction_id"])
            if not extractions.get(row["variable_value"]):
                extractions[row["variable_value"]] = {
                    "confidence": row["confidence"],
                    "extractions": [extraction]
                }
            else:
                extractions[row["variable_value"]
                            ]["extractions"].append(extraction)
        for key in extractions.keys():
            extractions[key]["agreement"] = agreement(
                extractions[key]["extractions"])
        return jsonify(extractions)

    @app.route('/api/get_variable_list', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def get_variable_list():
        output = query_db(
            get_db(), f"SELECT DISTINCT	variable_name FROM variable")
        return jsonify([v["variable_name"] for v in output])

    @app.route('/api/submit_answer/<extraction_id>/<answer>', methods=['POST', 'GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def submit_answer(extraction_id: int, answer: str):
        db = get_db()
        query_db(db,
                 f"UPDATE extraction SET valid='{answer}' WHERE extraction_id={extraction_id}")
        db.commit()
        return "OK"

    @app.route('/api/submit_explaination/<extraction_id>/<explaination>', methods=['POST', 'GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def submit_explaination(extraction_id: int, explaination: str):
        db = get_db()
        query_db(db,
                 f"UPDATE extraction SET validated_context='{explaination}' WHERE extraction_id={extraction_id}")
        db.commit()
        return "OK"

    @app.route('/api/download_data/', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def download_data():
        db = get_db()
        # get all docs
        docs = query_db(db, "SELECT document_name, document_id FROM document")
        doc_df = pd.DataFrame(docs)

        # Get all variables
        vars = query_db(
            db, "SELECT variable_id, variable_name, variable_value, document_id FROM variable")
        vars_df = pd.DataFrame(vars)
        # Get all extractions
        extractions = query_db(
            db, "SELECT extraction_id, valid, variable_id FROM extraction WHERE valid='TRUE'")
        extractions_df = pd.DataFrame(extractions)

        # merge
        df = pd.merge(doc_df, vars_df, on="document_id", how="left")
        df = pd.merge(df, extractions_df, on="variable_id", how="left")

        # New Dataframe: each row is a document/variable with a list of validated values
        df = df.groupby(["document_name", "variable_name"]).apply(
            lambda x: x[x["valid"] == "TRUE"]["variable_value"].tolist()).to_frame("validated_vals").reset_index()

        # Pivot out the variables, making each column correspond to a variable, and each row a document.
        df = df.pivot(index="document_name", columns=[
                      "variable_name"], values=["validated_vals"], ).reset_index()
        df.columns = df.columns.droplevel(0)
        df.rename(columns={'': 'document_name'}, inplace=True)
        return df.to_csv(index=False)

    @app.route('/api/update_confidence/', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def update_conf():
        db = get_db()
        update_confidence(db)
        return "OK"

    @app.route('/api/get_cases', methods=['GET'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
    def get_case_names():
        db = get_db()
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
        db = get_db()
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
    return app


@click.command("run")
@click.option("--db_path", type=str, default=Path(__file__).parents[2] / "database" / "test_db.sqlite")
def run_server(db_path: str):
    """Clear the existing data and create new tables."""
    app = create_app(Path(db_path))
    app.run(debug=True)


if __name__ == '__main__':
    run_server()
