import unittest
from tensorflow.keras.layers import Dense, LSTM
from helpers.ml import create_target, transform_rnn_sequences, split_dataframe_on_columns, build_model
import pandas as pd
import numpy as np


class TestCreateTarget(unittest.TestCase):

    def setUp(self):
        self.mock_data = pd.DataFrame(
            data=[[1, 2], [2, 0], [3, 4], [5, -1]],
            columns=['foo', 'close']
        )

    def test_transform(self):
        res = create_target(self.mock_data)
        self.assertEqual(res.columns.tolist(), ['foo', 'close', 'target'])
        self.assertEqual(res.iloc[0, 2], 2)
        self.assertEqual(res.iloc[2, 2], 4)


class TestTransformRNNSequences(unittest.TestCase):

    def setUp(self):
        self.mock_array_x = np.array([
            [1, 2],
            [2, 3],
            [4, 5],
            [99, 2]
        ])
        self.mock_array_y = np.array([
            [0],
            [1],
            [2],
            [3]
        ])
        self.long_mock_array_x = np.zeros((100, 100))
        self.long_mock_array_y = np.zeros((100, 1))

    def test_transform(self):
        res = transform_rnn_sequences(self.mock_array_x, self.mock_array_y, lookback=2, lookahead=1)
        self.assertEqual(res[0].shape, (2, 2, 2))
        self.assertEqual(res[1].shape, (2, 1))
        self.assertEqual(res[0][0, 1, 0], 2)
        self.assertEqual(res[0][0, 1, 1], 3)

    def test_transform_long(self):
        res = transform_rnn_sequences(self.long_mock_array_x, self.long_mock_array_y, lookback=36, lookahead=24)
        self.assertEqual(res[0].shape, (41, 36, 100))
        self.assertEqual(res[1].shape, (41, 24))


class TestSplitDataframe(unittest.TestCase):

    def setUp(self):
        self.mock_data = pd.DataFrame(
            data=[[1, 2], [2, 0], [3, 4], [5, -1]],
            columns=['foo', 'close']
        )

    def test_split_dataframe_on_columns(self):
        res = split_dataframe_on_columns(self.mock_data, ['close'])
        self.assertEqual(res[0].columns.tolist(), ['foo'])
        self.assertEqual(res[1].columns.tolist(), ['close'])
        self.assertEqual(res[0].shape[0], self.mock_data.shape[0])


class TestBuildModel(unittest.TestCase):

    def test_return_type(self):
        model = build_model()
        self.assertEqual(type(model.layers[0]), LSTM)
        self.assertEqual(type(model.layers[-1]), Dense)
