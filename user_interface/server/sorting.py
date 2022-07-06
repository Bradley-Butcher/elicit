from typing import Dict, List, Tuple, Union
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np

from database.db_utils import query_db


def set_confidence(db, variable_id: int, confidence: float):
    query_db(
        db, f"UPDATE variable SET value_confidence={'NULL' if confidence == '?' else confidence} WHERE variable_id={variable_id}")
    db.commit()


def get_variables(db):
    variables = query_db(
        db, f"SELECT DISTINCT variable_name FROM variable")
    return [v[0] for v in variables]


def get_data(db, variable_name: str):
    extraction_df = pd.read_sql(
        "SELECT method, confidence, valid, variable_id, document_id, extraction_id FROM extraction", db, index_col="extraction_id")
    variable_df = pd.read_sql(
        "SELECT variable_id, document_id, variable_name, variable_value, value_confidence FROM variable", db, index_col="variable_id")
    df = pd.merge(extraction_df, variable_df, on=[
                  "variable_id", "document_id"], how="left")
    df = df[df.variable_name == variable_name]
    return df


def get_variable_data(ext_var_df: pd.DataFrame, training: bool = False, include_value: bool = False):
    methods = ext_var_df.method.unique().tolist()
    df = ext_var_df.pivot(index=["document_id", "variable_id",
                          "variable_value", "valid"], columns="method", values="confidence").reset_index()

    if include_value:
        encoder = OneHotEncoder()
        encoder.fit(df.variable_value.values.reshape(-1, 1))
        OH_val = encoder.transform(df.variable_value.values.reshape(-1, 1))
        df = pd.concat([df, pd.DataFrame(OH_val.toarray().astype(int),
                       columns=encoder.get_feature_names().tolist())], axis=1)

    if training:
        df = df[~df.valid.isnull()]

    df = df.fillna(0)

    X = df[methods] if not include_value else df[methods +
                                                 encoder.get_feature_names().tolist()]
    y = (df["valid"] == "TRUE").astype(int)
    return df["variable_id"], X, y


def update_confidence(db, include_value: bool = False):
    for variable in get_variables(db):
        data = get_data(db, variable)
        _, X_train, y_train = get_variable_data(
            data, training=True, include_value=include_value)
        var_ids, X_dep, _ = get_variable_data(
            data, training=False, include_value=include_value)
        clf = LogisticRegression(solver="lbfgs")
        clf.fit(X_train, y_train)
        confidence = clf.predict_proba(X_dep)[:, 1]
        for i, var_id in enumerate(var_ids):
            set_confidence(db, var_id, confidence[i])
