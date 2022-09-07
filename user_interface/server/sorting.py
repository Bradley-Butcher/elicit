from typing import Dict, List, Tuple, Union
from typing_extensions import Literal
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np
from user_interface.server.label_model import LabelModel

from database.db_utils import query_db


def set_value_confidence(db, variable_id: int, confidence: float):
    query_db(
        db, f"UPDATE variable SET value_confidence={'NULL' if confidence == '?' else confidence} WHERE variable_id={variable_id}")
    db.commit()


def set_meta_confidence(db, extraction_id: int, confidence: float):
    query_db(
        db, f"UPDATE extraction SET meta_confidence={'NULL' if confidence == '?' else confidence} WHERE extraction_id={extraction_id}")
    db.commit()


def get_variables(db):
    variables = query_db(
        db, f"SELECT DISTINCT variable_name FROM variable")
    return [v[0] for v in variables]


def get_data(db, variable_name: str, include_value: bool = True):
    extraction_df = pd.read_sql(
        "SELECT meta_confidence, valid, variable_id, document_id, extraction_id FROM extraction", db)
    variable_df = pd.read_sql(
        "SELECT variable_id, document_id, variable_name, variable_value, value_confidence FROM variable", db)
    raw_extraction_df = pd.read_sql(
        "SELECT raw_extraction_id, extraction_id, method, confidence FROM raw_extraction", db)
    df = pd.merge(extraction_df, variable_df, on=[
                  "variable_id", "document_id"], how="left")
    df = pd.merge(raw_extraction_df, df, on=["extraction_id"], how="left")
    df = df[df.variable_name == variable_name]
    if include_value:
        return [df[df.variable_value == variable_value] for variable_value in df.variable_value.unique()]
    return df


def get_variable_data(ext_var_df: pd.DataFrame, training: bool = False):
    methods = ext_var_df.method.unique().tolist()
    methods = [m for m in methods if m != "manual"]
    df = ext_var_df.pivot(index=["document_id", "variable_id", "extraction_id",
                          "variable_value", "valid"], columns="method", values="confidence").reset_index()

    if training:
        df = df[~df.valid.isnull()]

    df = df.fillna(0)

    X = df[methods].astype(float)
    y = df["valid"].map({"TRUE": 1, "FALSE": 0}).fillna(-1)
    return df["extraction_id"], X, y


def _logistic_regression(X_train, y_train, X_dep):
    clf = LogisticRegression(solver="lbfgs")
    clf.fit(X_train, y_train)
    return clf.predict_proba(X_dep)[:, 1]


def _weasul(label_matrix, class_balance, labels):
    label_model = LabelModel()
    clique_matrix = [[i] for i in range(label_matrix.shape[1])]
    label_model.fit(label_matrix, clique_matrix, class_balance, labels)
    label_model.active_learning = True
    label_model.ground_truth_labels = labels
    label_model.penalty_strength = 0.1
    label_model.fit(label_matrix, clique_matrix,
                    class_balance, labels)
    return label_model.predict()[:, 0]


def get_metaconf_data(db, k: int = 3):
    def _topk(df: pd.DataFrame):
        top_vals = df.sort_values(
            "meta_confidence", ascending=False).head(k).reset_index()
        dict_vals = {f"value_{i}": top_vals.loc[i, "meta_confidence"] if len(
            top_vals) > i else 0 for i in range(k)}
        return pd.DataFrame({
            "id": df.variable_id,
            "variable_name": df.variable_name,
            "variable_value": df.variable_value,
            **dict_vals,
            "valid": df.valid})

    def _valid_filter(df):
        if df.valid.any():
            return df
        else:
            return None

    for variable in get_variables(db):
        var_data = get_data(db, variable, include_value=False)
        var_data["valid"] = var_data.valid.map({"TRUE": True, "FALSE": False})
        var_data["meta_confidence"] = var_data.meta_confidence.astype(float)
        val_data = var_data.groupby(
            ["document_id", "variable_name", "variable_value"]).apply(_topk)
        val_data.fillna(0, inplace=True)
        val_train_data = val_data[val_data.valid.notnull()]
        yield val_train_data, val_data


def learn_meta_classifier(db, k: int = 3):
    for train_data, data in get_metaconf_data(db, k=k):
        try:
            ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
            X_val = ohe.fit_transform(train_data[["variable_value"]])
            X = train_data[[f"value_{i}" for i in range(k)]]
            y = train_data.valid.astype(int)
            X = np.concatenate([X_val, X], axis=1)
            clf = LogisticRegression(solver="lbfgs")
            clf.fit(X, y)
            X_dep = ohe.transform(data[["variable_value"]])
            X_dep = np.concatenate(
                [X_dep, data[[f"value_{i}" for i in range(k)]]], axis=1)
            for i, idx in enumerate(data.id):
                set_value_confidence(db, idx, clf.predict_proba(X_dep)[i, 1])
        except:
            continue


def update_confidence(db, method: Literal['lr', 'weasul'] = "weasul", **kwargs):
    for variable in get_variables(db):
        for data in get_data(db, variable, True):
            _, X_train, y_train = get_variable_data(
                data, training=True)
            ex_ids, X_dep, y_dep = get_variable_data(
                data, training=False)

            if len(X_dep.columns) == 0:
                continue

            if method == "lr":
                confidence = _logistic_regression(X_train, y_train, X_dep)
            if method == "weasul":
                class_balance = kwargs.get("class_balance", None)
                if class_balance is None:
                    class_balance_var = np.array([0.5, 0.5])
                else:
                    class_balance_var = class_balance.get(variable, None)
                    if class_balance_var is None:
                        class_balance_var = np.array([1, 1])
                confidence = _weasul(X_dep.values, class_balance_var, y_dep)
            else:
                raise ValueError("Invalid method")

            for i, ex_id in enumerate(ex_ids):
                set_meta_confidence(db, ex_id, confidence[i])
