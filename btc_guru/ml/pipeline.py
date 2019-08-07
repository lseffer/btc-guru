from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model
from ml.helpers import (create_preprocess_pipeline, extract_features,
                        split_dataframe_on_columns, transform_rnn_sequences,
                        build_model)
from helpers.database import InfluxdbQuery
from typing import Tuple
import numpy as np
import joblib
from etl.influxdb_etl import InfluxdbETL

# Job for training the preprocessor and model
# 

# ETL for getting data, running preprocessing and writing predictions to database
# Need to save timestamps for prediction for writing to database
# Need to gracefully exit if there are no saved models

class MLETL(InfluxdbETL):

    def __init__(self):
        super(MLETL).__init__()
        try:
            self.model = load_model('rnn_model.h5')
            self.preprocess_pipeline = joblib.load('preprocess_pipeline.pkl')
        except (OSError, FileNotFoundError):
            self.model = None
            self.preprocess_pipeline = None

    def extract(self):
        if self.preprocess_pipeline is None:
            return []
        input_data = InfluxdbQuery(dict(fields='open,high,low,close,volume'), 100000).query()
        input_data = input_data.sort_values(by='time', ascending=True).set_index('time')
        input_data_features = extract_features(input_data)
        dataframe_x, dataframe_y = split_dataframe_on_columns(input_data_features, ['target'])
        X = preprocess_pipeline.transform(dataframe_x.values)

    def transform(self, data):
        if self.model is None:
            return []

class MLPipeline():




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

    rnn_model.save('rnn_model.h5')
    return rnn_model, X_val, rnn_model.predict(X_val), y_val


if __name__ == '__main__':
    from ml.pipeline import train_model
    asd = train_model()
    import numpy as np
    print(((np.sign(asd[2]) > 0.5) * 1.0 == ((np.sign(asd[3][:, 0].reshape(-1, 1)) > 0.5) * 1.0)).sum() / asd[2].shape[0])
    print(np.quantile(asd[2], [0.1, 0.9]), np.quantile(asd[3][:, 0], [0.1, 0.9]))
