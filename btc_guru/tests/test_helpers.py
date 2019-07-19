import unittest
from helpers import grouper
from helpers.database import InfluxdbApiQuery
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
        influxapi = InfluxdbApiQuery()
        self.assertEqual(influxapi.request_parameters, {})
        self.assertEqual(influxapi.measurement, 'ohlcv')
        self.assertEqual(influxapi.fields, '*')
        self.assertEqual(influxapi.asset, 'btc')

    def test_transform_dataframe(self):
        influxapi = InfluxdbApiQuery()
        output_data = influxapi._transform_dataframe(self.input_data)
        self.assertEqual(set(output_data.columns.tolist()), set(['time', 'a', 'b']))
        self.assertEqual(len(self.input_data), len(output_data))

    @mock.patch("helpers.database.create_influxdb_dataframe_client")
    def test_query_empty_res(self, mock_create):
        mock_create.return_value.query = lambda x: {}
        influxapi = InfluxdbApiQuery()
        res = influxapi.query()
        self.assertEqual(res, "No data returned, check your query parameters")

    @mock.patch("helpers.database.create_influxdb_dataframe_client")
    def test_query(self, mock_create):
        mock_create.return_value.query = lambda x: {'ohlcv': self.input_data}
        influxapi = InfluxdbApiQuery()
        res = influxapi.query()
        self.assertEqual(res, '{"columns":["time","a","b"],"data":[[0,1,2],[1,2,3]]}')
