from tensorflow.keras.layers import Dense, LSTM, Input
from tensorflow.keras import Sequential
import tensorflow_probability as tfp

def build_model():
    model = Sequential()
    model.add(Input(shape=(30, 30)))
    model.add(LSTM(10))
    model.add(Dense(16))
    model.add(tfp.layers.DenseFlipout(1))
    return model
