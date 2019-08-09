from pandas import DataFrame
from typing import Tuple, List
from ta.wrapper import add_all_ta_features
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
from tensorflow.keras.layers import Dense, LSTM, Input
from tensorflow.keras import Sequential
import tensorflow_probability as tfp


def build_model(input_shape=(30, 30), recurrent_layers=1, dense_layers=1, bayesian=False, activation='linear'):
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(16, input_shape=input_shape))
    for _ in range(recurrent_layers - 1):
        model.add(LSTM(16))
    for _ in range(dense_layers):
        model.add(Dense(32))
    if bayesian:
        model.add(tfp.layers.DenseFlipout(1, activation=activation))
    else:
        model.add(Dense(1, activation=activation))
    model.compile(
        optimizer='adam',
        loss='logcosh')
    return model


def create_preprocess_pipeline():
    return Pipeline([
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='median')),
        ('scaler', MinMaxScaler())
    ])


def split_dataframe_on_columns(dataframe: DataFrame, column_names: List) -> Tuple[DataFrame, DataFrame]:
    return (dataframe.loc[:, ~dataframe.columns.isin(column_names)],
            dataframe.loc[:, dataframe.columns.isin(column_names)][column_names])


def create_target(dataframe: DataFrame, lookahead=24) -> DataFrame:
    dataframe.loc[:, 'target'] = dataframe["close"] \
        .pct_change(periods=lookahead) \
        .shift(-lookahead)
    return dataframe


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
    y_reshaped: np.ndarray = np.zeros((samples, y.shape[1]))

    for i in range(samples):
        y_position = i + lookback
        X_reshaped[i] = X[i:y_position]
        y_reshaped[i] = y[y_position - 1]

    return X_reshaped, y_reshaped
