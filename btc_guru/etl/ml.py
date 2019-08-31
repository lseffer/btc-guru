from tensorflow.keras.models import load_model
from helpers.ml import (extract_features,
                        split_dataframe_on_columns, transform_rnn_sequences)
from helpers.ml.tools import MLTools
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
        self.last_time_point = None
        self.last_close_value = None
        try:
            self.model = load_model(MLTools.rnn_model_path)
            self.preprocess_pipeline = joblib.load(MLTools.preprocess_pipeline_path)
            self.target_scaler = joblib.load(MLTools.target_scaler_path)
        except (OSError, FileNotFoundError):
            self.model = None
            self.preprocess_pipeline = None

    def extract(self) -> ndarray:
        if self.preprocess_pipeline is None:
            return
        input_data = InfluxdbQuery(dict(fields='open,high,low,close,volume',
                                        result_limit=MLTools.lookback * 2)).query()
        input_data = input_data.sort_values(by='time', ascending=True).set_index('time')
        input_data_features = extract_features(input_data)
        dataframe_x, dataframe_y = split_dataframe_on_columns(input_data_features, ['target'])
        X = self.preprocess_pipeline.transform(dataframe_x.values)
        X_rnn, _ = transform_rnn_sequences(X, dataframe_y.values, lookback=MLTools.lookback)
        self.last_time_point = input_data.index.values[-1]
        self.last_close_value = input_data["close"].values[-1]
        return X_rnn[-1:]

    def transform(self, data: ndarray) -> List[Dict]:
        if self.model is None or self.last_time_point is None or data is None:
            return []
        data_transformed = []
        predictions = self.model.predict(data).reshape(-1, 1)
        for i in range(predictions.shape[0]):
            json_body = InfluxdbModel(
                measurement="ohlcv",
                tags={
                    "asset": "btc"
                },
                time=(datetime.fromtimestamp(self.last_time_point.astype(
                    datetime) * 1e-9) + timedelta(hours=i + 1)).isoformat(),
                fields={
                    "predicted_close_absolute": self.target_scaler.inverse_transform(predictions[i].reshape(-1, 1))[0][0],
                    "predicted_close_relative": 0.0
                }
            ).schema
            data_transformed.append(json_body)
        return data_transformed
