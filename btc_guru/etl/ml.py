from tensorflow.keras.models import load_model
from helpers.ml import (extract_features,
                        split_dataframe_on_columns, transform_rnn_sequences)
from helpers.ml.train_model import MLTools
from helpers.database import InfluxdbQuery
from helpers.models import InfluxdbModel
from typing import List, Dict
from numpy import ndarray
import joblib
from etl.influxdb_etl import InfluxdbETL
from datetime import datetime, timedelta


class MLETL(InfluxdbETL, MLTools):

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
        input_data = InfluxdbQuery(dict(fields='open,high,low,close,volume'), MLTools.lookback * 2).query()
        input_data = input_data.sort_values(by='time', ascending=True).set_index('time')
        self.close_values = input_data["close"].values
        input_data_features = extract_features(input_data)
        dataframe_x, dataframe_y = split_dataframe_on_columns(input_data_features, ['target'])
        X = self.preprocess_pipeline.transform(dataframe_x.values)
        X_rnn, _ = transform_rnn_sequences(X, dataframe_y.values, lookback=MLTools.lookback)
        self.time_points = input_data.index.values[-X_rnn.shape[0]:]
        return X_rnn

    def transform(self, data: ndarray) -> List[Dict]:
        if self.model is None or self.time_points is None or data is None:
            return []
        data_transformed = []
        predictions = self.model.predict(data).reshape(-1, 1)
        for i in range(predictions.shape[0]):
            json_body = InfluxdbModel(
                measurement="ohlcv",
                tags={
                    "asset": "btc"
                },
                time=(datetime.fromtimestamp(self.time_points[i].astype(
                    datetime) * 1e-9) + timedelta(hours=MLTools.lookahead)).isoformat(),
                fields={
                    "predicted_close_absolute": (1 + predictions[i, 0]) * self.close_values[i],
                    "predicted_close_relative": predictions[i, 0]
                }
            ).schema
            data_transformed.append(json_body)
        return data_transformed
