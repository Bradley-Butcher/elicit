from typing import Dict, List, Tuple, Union
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np

def get_methods(extractions: List[Dict[str, Union[str, float, int]]]) -> List[str]:
    first_variable = extractions[0].variable_id
    methods = []
    for e in extractions:
        if e.variable_id != first_variable:
            break
        methods.append(e.method)

def dfs_to_data(variable_df, extraction_df, encoder):
    def _get_response(variable_id: int, column: str):
        return variable_df[variable_df.variable_id == variable_id][column].values[0]
    X = extraction_df.pivot(index='variable_id', columns='method', values='confidence').reset_index(level=0)
    var_values = X.variable_id.apply(lambda x: _get_response(x, "variable_value"))
    # X = pd.concat([X, pd.DataFrame(encoder.transform(var_values.values.reshape(-1, 1)).toarray(), dtype=int)], axis=1)
    # convert all to floats or ints
    X = X.apply(pd.to_numeric, errors='ignore')
    y = X.variable_id.apply(lambda x: 1 if _get_response(x, "human_response") == "correct" else 0)
    return X.values, y.values

def build_data(variables: List[Dict[str, Union[str, float, int]]], extractions: List[Dict[str, Union[str, float, int]]]) -> Tuple[List[float], int]:
    """Convert from database form to X,y form."""
    encoder = OneHotEncoder()
    encoder.fit(variables.variable_value.values.reshape(-1, 1))
    variable_df_train = variables[variables.human_response.notnull()]
    extraction_df_train = extractions[extractions.variable_id.isin(variable_df_train.variable_id)]
    X, _ = dfs_to_data(variables, extractions, encoder)
    X_train, y_train = dfs_to_data(variable_df_train, extraction_df_train, encoder)
    return X_train, y_train, X

def get_confidence(variables: List[Dict[str, Union[str, float, int]]], extractions: List[Dict[str, Union[str, float, int]]]) -> List[float]:
    """
    Train the classifier.

    Args:
        X: A list of lists of features.
        y: A list of labels.

    Returns:
        A trained classifier.
    """
    extractions = pd.DataFrame(extractions)
    variables = pd.DataFrame(variables)
    indicies = list(variables.variable_id.values)
    values = ["?" for _ in range(len(variables))]
    for variable_type in set(variables.variable_name.values):
        local_variables = variables[variables.variable_name == variable_type]
        local_extractions = extractions[extractions.variable_id.isin(local_variables.variable_id)]
        if len(local_variables[local_variables.human_response.notnull()]) <= 3:
            continue
        X_train, y_train, X = build_data(local_variables, local_extractions)
        clf = LogisticRegression()
        clf.fit(np.nan_to_num(X_train[:, 1:], 0), y_train)
        for i, val in zip(X[:, 0], clf.predict_proba(np.nan_to_num(X[:, 1:], 0))[:, 1]):
            values[indicies.index(i)] = val
    return indicies, values