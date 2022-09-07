from typing import Callable
from typing_extensions import Literal
import pandas as pd
from database.db_utils import get_variables


def agreement(df: pd.DataFrame):
    df["lf_confidence"] = df["lf_confidence"].astype(float)
    df = df.groupby(["document_id", "variable_name", "variable_value", "extraction_id"]).agg(
        {"lf_confidence": "sum", "valid": "first"}).reset_index()
    grouped = df.groupby(["document_id", "variable_name", "variable_value"])
    df = df.loc[grouped['lf_confidence'].idxmax()]
    grouped = df.groupby(["document_id", "variable_name"])
    df = df.loc[grouped['lf_confidence'].idxmax()]
    return df


def meta_confidence(df: pd.DataFrame):
    df["meta_confidence"] = df["meta_confidence"].astype(float)
    df["meta_confidence"] = df["meta_confidence"].fillna(0)
    max_idx = df.groupby(["document_id", "variable_name", "variable_value"])[
        "meta_confidence"].idxmax()
    df = df.loc[max_idx]
    grouped = df.groupby(["document_id", "variable_name"])
    df = df.loc[grouped['meta_confidence'].idxmax()]
    return df


def confidence(df: pd.DataFrame):
    df['value_confidence'] = df['value_confidence'].astype(float)
    df["value_confidence"] = df["value_confidence"].fillna(0)
    grouped = df.groupby(["document_id", "variable_name"])
    filtered = df.loc[grouped['value_confidence'].idxmax()]
    return filtered


def get_variables_data(db):
    extraction_df = pd.read_sql(
        "SELECT meta_confidence, valid, variable_id, document_id, extraction_id FROM extraction", db)
    variable_df = pd.read_sql(
        "SELECT variable_id, document_id, variable_name, variable_value, value_confidence FROM variable", db)
    raw_extraction_df = pd.read_sql(
        "SELECT raw_extraction_id, extraction_id, method, confidence as lf_confidence FROM raw_extraction", db)
    df = pd.merge(extraction_df, variable_df, on=[
        "variable_id", "document_id"], how="left")
    df["valid"] = df["valid"].map({"TRUE": True, "FALSE": False})
    valid_df = df.groupby(["document_id", "variable_id"]).agg(
        {"valid": "any"}).reset_index()
    df = df.drop(columns=["valid"])
    df = pd.merge(df, valid_df, on=["document_id", "variable_id"], how="left")
    df = pd.merge(raw_extraction_df, df, on=["extraction_id"], how="left")
    for variable in df.variable_name.unique():
        yield df[df["variable_name"] == variable], variable


def _performance_caller(db, performance_func: Callable):
    select = ["document_id", "variable_name", "variable_value"]
    variable_performance = {}
    for df, variable in get_variables_data(db):
        predicted_rows = performance_func(df)
        variable_performance[variable] = predicted_rows.valid.sum(
        ) / len(predicted_rows)
    return variable_performance


def performance(db, performance_type: Literal["agreement", "confidence", "meta_confidence"]):
    if performance_type == "agreement":
        return _performance_caller(db, agreement)
    elif performance_type == "confidence":
        return _performance_caller(db, confidence)
    elif performance_type == "meta_confidence":
        return _performance_caller(db, meta_confidence)
    else:
        raise ValueError(
            "performance_type must be `agreement` or `confidence`")
