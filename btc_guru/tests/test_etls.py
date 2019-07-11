import unittest
from etl.coinapi import CoinApiETL
from etl.initialize_database import CryptoDataDownloadETL
import pandas as pd


class CoinApiETLTest(unittest.TestCase):

    def setUp(self):
        self.capi = CoinApiETL()

    def test_endpoint(self):
        self.assertEqual(self.capi.endpoint,
                         "https://rest.coinapi.io/v1/ohlcv/GEMINI_SPOT_BTC_USD/history")

    def test_request_parameters(self):
        self.assertEqual(dict(
            period_id='1HRS',
            time_start='2019-07-01T01:00:00',
            time_end='2019-07-02T00:00:00'
        ), self.capi._create_request_parameters())

    def test_transform(self):
        data = [{
            "time_period_end": "2019-01-01T00:00:00",
            "price_open": 12.0,
            "price_high": 12.0,
            "price_low": 12.0,
            "price_close": 12.0,
            "volume_traded": 100.0}]
        expected_result = [{
            "measurement": "ohlcv",
            "tags": {
                "asset": "btc"
            },
            "time": "2019-01-01T00:00:00",
            "fields": {
                    "open": 12.0,
                    "high": 12.0,
                    "low": 12.0,
                    "close": 12.0,
                    "volume": 100.0
            }
        }]
        self.assertEqual(
            expected_result,
            self.capi.transform(data)
        )


class CryptoDataDownloadETLTest(unittest.TestCase):

    def setUp(self):
        self.cdd = CryptoDataDownloadETL()

    def test_transform(self):
        data = pd.DataFrame([{
            "Date": "2019-01-01T00:00:00",
            "Open": 12.0,
            "High": 12.0,
            "Low": 12.0,
            "Close": 12.0,
            "Volume": 100.0}])
        expected_result = [{
            "measurement": "ohlcv",
            "tags": {
                "asset": "btc"
            },
            "time": "2019-01-01T00:00:00",
            "fields": {
                    "open": 12.0,
                    "high": 12.0,
                    "low": 12.0,
                    "close": 12.0,
                    "volume": 100.0
            }
        }]
        self.assertEqual(
            expected_result,
            self.cdd.transform(data)
        )
