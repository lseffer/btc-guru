from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model, save_model
from ml.helpers import (create_preprocess_pipeline, extract_features,
                        split_dataframe_on_columns, transform_rnn_sequences,
                        build_model)
from helpers.database import InfluxdbQuery
from helpers.models import InfluxdbModel
from typing import List, Dict
import numpy as np
from numpy import ndarray
import joblib
from etl.influxdb_etl import InfluxdbETL
from datetime import datetime, timedelta

# Job for training the preprocessor and model
#

# ETL for getting data, running preprocessing and writing predictions to database
# Need to save timestamps for prediction for writing to database
# Need to gracefully exit if there are no saved models


class MLETL(InfluxdbETL):

    def __init__(self):
        super().__init__()
        self.time_points = None
        self.close_values = None
        try:
            self.model = load_model('rnn_model.h5')
            self.preprocess_pipeline = joblib.load('preprocess_pipeline.pkl')
        except (OSError, FileNotFoundError):
            self.model = None
            self.preprocess_pipeline = None

    def extract(self) -> ndarray:
        if self.preprocess_pipeline is None:
            return
        input_data = InfluxdbQuery(dict(fields='open,high,low,close,volume'), 96).query()
        input_data = input_data.sort_values(by='time', ascending=True).set_index('time')
        self.close_values = input_data["close"].values
        self.time_points = input_data.index.values
        input_data_features = extract_features(input_data)
        dataframe_x, dataframe_y = split_dataframe_on_columns(input_data_features, ['target'])
        X = self.preprocess_pipeline.transform(dataframe_x.values)
        X_rnn, _ = transform_rnn_sequences(X, dataframe_y.values, lookback=48)
        return X_rnn

    def transform(self, data: ndarray) -> List[Dict]:
        if self.model is None or self.time_points is None or data is None:
            return []
        data_transformed = []
        predictions = self.model.predict(data).reshape(-1, 1)
        for i in range(predictions.shape[0]):
            json_body = InfluxdbModel(
                measurement="predictions",
                tags={
                    "asset": "btc"
                },
                time=(datetime.fromtimestamp(self.time_points[i].astype(
                    datetime) * 1e-9) + timedelta(hours=24)).timestamp(),
                fields={
                    "close_absolute": (1 + predictions[i, 0]) * self.close_values[i],
                    "close_relative": predictions[i, 0]
                }
            ).schema
            data_transformed.append(json_body)
        return data_transformed


def train_model():
    preprocess_pipeline = create_preprocess_pipeline()
    input_data = InfluxdbQuery(dict(fields='open,high,low,close,volume'), 100000).query()
    input_data = input_data.sort_values(by='time', ascending=True).set_index('time')
    input_data_features = extract_features(input_data)
    dataframe_x, dataframe_y = split_dataframe_on_columns(input_data_features, ['target'])
    X_train, X_val, y_train, y_val = train_test_split(dataframe_x.values, dataframe_y.values,
                                                      test_size=0.03, random_state=42, shuffle=True)

    X_train = preprocess_pipeline.fit_transform(X_train)
    X_val = preprocess_pipeline.transform(X_val)

    X_train, y_train = transform_rnn_sequences(X_train, y_train, lookback=48)
    X_val, y_val = transform_rnn_sequences(X_val, y_val, lookback=48)

    joblib.dump(preprocess_pipeline, 'preprocess_pipeline.pkl')

    rnn_model = build_model(input_shape=X_train.shape[1:])
    rnn_model.fit(X_train, y_train,
                  validation_data=(X_val, y_val),
                  epochs=30,
                  batch_size=32,
                  callbacks=[EarlyStopping(restore_best_weights=True, patience=2)])

    save_model(rnn_model, 'rnn_model.h5')
    return rnn_model, X_val, rnn_model.predict(X_val), y_val


if __name__ == '__main__':
    from ml.pipeline import train_model
    asd = train_model()
    import numpy as np
    print(((np.sign(asd[2]) > 0.5) * 1.0 ==
           ((np.sign(asd[3][:, 0].reshape(-1, 1)) > 0.5) * 1.0)).sum() / asd[2].shape[0])
    print(np.quantile(asd[2], [0.1, 0.9]), np.quantile(asd[3][:, 0], [0.1, 0.9]))
