from tensorflow.keras.models import save_model
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from helpers.ml import (extract_features, create_preprocess_pipeline, build_model,
                        split_dataframe_on_columns, transform_rnn_sequences,
                        create_target_scaler)
from helpers.database import InfluxdbQuery
from config import HOME
import pandas as pd
import joblib
import os


class MLTools():

    lookback = 48
    lookahead = 24
    binary_dir = os.path.join(HOME, 'btc_guru', 'bin')
    preprocess_pipeline_path = os.path.join(binary_dir, 'preprocess_pipeline.pkl')
    target_scaler_path = os.path.join(binary_dir, 'target_scaler.pkl')
    rnn_model_path = os.path.join(binary_dir, 'rnn_model.h5')

    @staticmethod
    def train_model() -> None:
        target_scaler = create_target_scaler()
        preprocess_pipeline = create_preprocess_pipeline()
        input_data = InfluxdbQuery(dict(fields='open,high,low,close,volume', result_limit=100000)).query()
        input_data = input_data.sort_values(by='time', ascending=True).set_index('time')
        input_data_features = extract_features(input_data, lookahead=MLTools.lookahead)
        input_data_features = input_data_features.pipe(lambda df: df[~pd.isna(df['target'])])
        dataframe_x, dataframe_y = split_dataframe_on_columns(input_data_features, ['target'])
        X_train, X_val, y_train, y_val = train_test_split(dataframe_x.values, dataframe_y.values,
                                                          test_size=0.03, random_state=42, shuffle=False)

        X_train = preprocess_pipeline.fit_transform(X_train)
        X_val = preprocess_pipeline.transform(X_val)

        y_train = target_scaler.fit_transform(y_train)
        y_val = target_scaler.transform(y_val)

        X_train, y_train = transform_rnn_sequences(X_train, y_train, lookback=MLTools.lookback,
            lookahead=MLTools.lookahead)
        X_val, y_val = transform_rnn_sequences(X_val, y_val, lookback=MLTools.lookback,
            lookahead=MLTools.lookahead)

        joblib.dump(preprocess_pipeline, MLTools.preprocess_pipeline_path)
        joblib.dump(target_scaler, MLTools.target_scaler_path)

        rnn_model = build_model(input_shape=X_train.shape[1:], output_neurons=y_train.shape[1])
        rnn_model.fit(X_train, y_train,
                      validation_data=(X_val, y_val),
                      epochs=30,
                      batch_size=32,
                      callbacks=[EarlyStopping(restore_best_weights=True, patience=2, monitor='val_loss')])

        save_model(rnn_model, MLTools.rnn_model_path)
