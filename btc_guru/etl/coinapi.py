import requests
from config import COINAPI_KEY
from etl.influxdb_etl import InfluxdbETL
from helpers.models import InfluxdbModel
from typing import Dict, List

COINAPI_HISTORY_URL = "https://rest.coinapi.io/v1/ohlcv/{symbol}/history"
COINAPI_SYMBOL = "{exchange_id}_SPOT_{asset_id_base}_{asset_id_quote}"


class CoinApiETL(InfluxdbETL):
    def __init__(self, exchange_id='GEMINI',
                 asset_id_base='BTC',
                 asset_id_quote='USD',
                 period_id='1HRS',
                 time_start='2019-07-01T01:00:00',
                 time_end='2019-07-02T00:00:00'):
        super().__init__()
        self.exchange_id = exchange_id
        self.asset_id_base = asset_id_base
        self.asset_id_quote = asset_id_quote
        self.period_id = period_id
        self.time_start = time_start
        self.time_end = time_end

    @property
    def endpoint(self) -> str:
        symbol = COINAPI_SYMBOL.format(exchange_id=self.exchange_id,
                                       asset_id_base=self.asset_id_base,
                                       asset_id_quote=self.asset_id_quote)
        return COINAPI_HISTORY_URL.format(symbol=symbol)

    def _create_request_parameters(self) -> Dict:
        return dict(
            period_id=self.period_id,
            time_start=self.time_start,
            time_end=self.time_end
        )

    def extract(self) -> List[Dict]:
        res: List[Dict] = requests.get(self.endpoint,
                                       params=self._create_request_parameters(),
                                       headers={"X-CoinAPI-Key": COINAPI_KEY}).json()
        return res

    def transform(self, data: List[Dict]):
        data_transformed = []
        for record in data:
            json_body = InfluxdbModel(  # type: ignore
                measurement="ohlcv",
                tags={
                    "asset": "btc"
                },
                time=record.get("time_period_end"),
                fields={
                    "open": record.get("price_open"),
                    "high": record.get("price_high"),
                    "low": record.get("price_low"),
                    "close": record.get("price_close"),
                    "volume": record.get("volume_traded")
                }
            ).schema
            data_transformed.append(json_body)
        return data_transformed


if __name__ == '__main__':
    capi = CoinApiETL()
    capi.job()
    # print(capi.get_data('1HRS', '2019-07-01T01:00:00', '2019-07-02T00:00:00').json())
