from tensorflow.keras.layers import Dense, LSTM, Input
from tensorflow.keras import Sequential
import tensorflow_probability as tfp


def build_model(input_shape=(30, 30), recurrent_layers=1, dense_layers=1, bayesian=False):
    model = Sequential()
    model.add(Input(shape=input_shape))
    for _ in range(recurrent_layers):
        model.add(LSTM(16))
    for _ in range(dense_layers):
        model.add(Dense(32))
    if bayesian:
        model.add(tfp.layers.DenseFlipout(1))
    else:
        model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model
