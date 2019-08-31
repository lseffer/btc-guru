from pandas import DataFrame
from typing import Tuple, List
from ta.wrapper import add_all_ta_features
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
from tensorflow.keras.layers import Dense, LSTM, Input
from tensorflow.keras import Sequential


def build_model(input_shape=(30, 30), output_neurons=30):
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(16, input_shape=input_shape, return_sequences=True, activation='relu'))
    model.add(LSTM(16, activation='relu'))
    model.add(Dense(output_neurons))
    model.compile(
        optimizer='adam',
        loss='logcosh')
    return model


def create_target_scaler():
    return MinMaxScaler()

def create_preprocess_pipeline():
    return Pipeline([
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='median')),
        ('scaler', MinMaxScaler())
    ])


def split_dataframe_on_columns(dataframe: DataFrame, column_names: List) -> Tuple[DataFrame, DataFrame]:
    return (dataframe.loc[:, ~dataframe.columns.isin(column_names)],
            dataframe.loc[:, dataframe.columns.isin(column_names)][column_names])


def create_target(dataframe: DataFrame) -> DataFrame:
    dataframe.loc[:, 'target'] = dataframe["close"]
    return dataframe


def extract_features(dataframe: DataFrame, lookahead=24) -> DataFrame:
    return dataframe \
        .pipe(create_target) \
        .pipe(add_all_ta_features, *['open', 'high', 'low', 'close', 'volume']) \
        .pipe(lambda df: df.replace([np.inf, -np.inf], np.nan))


def transform_rnn_sequences(X: np.ndarray, y: np.ndarray, lookback=36, lookahead=24) -> Tuple[np.ndarray, ...]:
    assert X.shape[0] == y.shape[0], "Array axis 0 need to be equal"

    samples = X.shape[0] - lookback - lookahead + 1

    X_reshaped: np.ndarray = np.zeros((samples, lookback, X.shape[1]))
    y_reshaped: np.ndarray = np.zeros((samples, lookahead))

    for i in range(samples):
        position_start = i + lookback
        position_end = position_start + lookahead
        X_reshaped[i] = X[i:position_start]
        y_reshaped[i] = y[position_start:position_end].flatten()

    return X_reshaped, y_reshaped
