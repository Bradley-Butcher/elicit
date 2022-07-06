from typing import Dict, List, Tuple, Union
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np

from database.db_utils import query_db


def set_confidence(db, variable_id, confidence):
    query_db(
        db, f"UPDATE variable SET confidence={'NULL' if confidence == '?' else confidence} WHERE variable_id={variable_id}")
    db.commit()


def get_variables(db):
    variables = query_db(
        db, f"SELECT DISTINCT variable_name FROM variable")
    return variables


def get_data(db, variable_name: str):
    extraction_df = pd.read_sql(
        "SELECT * FROM extraction", db, index_col="extraction_id")
    variable_df = pd.read_sql(
        "SELECT * FROM variable", db, index_col="variable_id")
    df = pd.merge(extraction_df, variable_df, on="variable_id", how="left")
    df = df[df.variable_name == variable_name]
    return df


def get_variable_data(ext_var_df:pd.DataFrame):
    df = ext_var_df.melt(
        id_vars=["document_id", "variable_id", "variable_value", "method"], value_vars=["confidence", "valid"])
    df = df[~df.valid.isnull()]


def update_confidence():
    
