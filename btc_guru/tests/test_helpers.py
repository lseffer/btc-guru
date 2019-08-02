import unittest
from helpers import grouper
from helpers.database import InfluxdbQuery
from helpers.models import InfluxdbModel
import pandas as pd
from unittest import mock


class HelpersTest(unittest.TestCase):

    def test_grouper(self):
        data = [1, 2, 3, 4, 5]
        grouped = grouper(data, 2)
        self.assertEqual([1, 2], list(next(grouped)))
        self.assertEqual([3, 4], list(next(grouped)))
        self.assertEqual([5, None], list(next(grouped)))
        with self.assertRaises(StopIteration):
            next(grouped)


class InfluxdbApiQueryTest(unittest.TestCase):

    def setUp(self):
        self.input_data = pd.DataFrame(data=[[1, 2], [2, 3]], columns=['a', 'b'])

    def test_init(self):
        influxapi = InfluxdbQuery()
        self.assertEqual(influxapi.request_parameters, {})
        self.assertEqual(influxapi.measurement, 'ohlcv')
        self.assertEqual(influxapi.fields, '*')
        self.assertEqual(influxapi.asset, 'btc')

    def test_transform_dataframe(self):
        influxapi = InfluxdbQuery()
        output_data = influxapi._transform_dataframe(self.input_data)
        self.assertEqual(set(output_data.columns.tolist()), set(['time', 'a', 'b']))
        self.assertEqual(len(self.input_data), len(output_data))

    @mock.patch("helpers.database.create_influxdb_dataframe_client")
    def test_query_empty_res(self, mock_create):
        mock_create.return_value.query = lambda x: {}
        influxapi = InfluxdbQuery()
        res = influxapi.query()
        self.assertEqual(res.shape, (0, 0))

    @mock.patch("helpers.database.create_influxdb_dataframe_client")
    def test_query(self, mock_create):
        mock_create.return_value.query = lambda x: {'ohlcv': self.input_data}
        influxapi = InfluxdbQuery()
        res = influxapi.query()
        self.assertEqual(res.columns.tolist(), ["time", "a", "b"])
        self.assertEqual(res.shape[0], 2)


class TestInfluxdbModel(unittest.TestCase):

    def test_create_default(self):
        res = InfluxdbModel()
        self.assertEqual(res.fields, {})
        self.assertEqual(res.tags, {})
        self.assertEqual(res.measurement, "")

    def test_create(self):
        time = 100.0
        fields = {'asd': 1}
        tags = {'asd': 1}
        measurement = 'asd'
        res = InfluxdbModel(time=time, fields=fields, tags=tags, measurement=measurement)
        self.assertEqual(res.fields, fields)
        self.assertEqual(res.tags, tags)
        self.assertEqual(res.measurement, measurement)
        self.assertEqual(res.schema["time"], 100.0)

    def test_immutable(self):
        time = 100.0
        fields = {'asd': 1}
        tags = {'asd': 1}
        measurement = 'asd'
        res = InfluxdbModel(time=time, fields=fields, tags=tags, measurement=measurement)
        with self.assertRaises(Exception):
            res.time = 10
