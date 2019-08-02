import pandas as pd
from etl.influxdb_etl import InfluxdbETL
from helpers.models import InfluxdbModel
from pandas import DataFrame
from typing import List, Dict


class CryptoDataDownloadETL(InfluxdbETL):

    def extract(self) -> DataFrame:
        return pd.read_csv('http://www.cryptodatadownload.com/cdd/gemini_BTCUSD_1hr.csv',
                           skiprows=1)

    def transform(self, data: DataFrame) -> List[Dict]:
        data_transformed = []
        for index, record in data.iterrows():
            json_body = InfluxdbModel(
                measurement="ohlcv",
                tags={
                    "asset": "btc"
                },
                time=record["Date"],
                fields={
                    "open": record["Open"],
                    "high": record["High"],
                    "low": record["Low"],
                    "close": record["Close"],
                    "volume": record["Volume"]
                }
            ).schema
            data_transformed.append(json_body)
        return data_transformed


if __name__ == '__main__':
    cdd_etl = CryptoDataDownloadETL()
    cdd_etl.job()
