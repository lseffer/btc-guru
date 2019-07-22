from pandas import DataFrame
from typing import Tuple
from ta.wrapper import add_all_ta_features
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer


def create_preprocess_pipeline():
    return Pipeline([
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='mean')),
        ('scaler', MinMaxScaler())
    ])


def split_dataframe_on_column(dataframe: DataFrame, column_name: str) -> Tuple[DataFrame, DataFrame]:
    return dataframe.loc[:, dataframe.columns != column_name], dataframe.loc[:, dataframe.columns == column_name]


def create_target(X: DataFrame, lookahead=36, column_name='target') -> DataFrame:
    X.loc[:, column_name] = X["close"] \
        .pct_change(periods=lookahead) \
        .shift(-lookahead)
    return X


def extract_features(dataframe: DataFrame) -> DataFrame:
    return dataframe \
        .pipe(create_target) \
        .pipe(add_all_ta_features, *['open', 'high', 'low', 'close', 'volume']) \
        .pipe(lambda df: df[~pd.isna(df['target'])]) \
        .pipe(lambda df: df.replace([np.inf, -np.inf], np.nan))


def transform_rnn_sequences(X: np.ndarray, y: np.ndarray, lookback=36) -> Tuple[np.ndarray, ...]:
    assert X.shape[0] == y.shape[0], "Array axis 0 need to be equal"

    samples = X.shape[0] - lookback + 1

    X_reshaped: np.ndarray = np.zeros((samples, lookback, X.shape[1]))
    y_reshaped: np.ndarray = np.zeros((samples))

    for i in range(samples):
        y_position = i + lookback
        X_reshaped[i] = X[i:y_position]
        y_reshaped[i] = y[y_position - 1]

    return X_reshaped, y_reshaped
