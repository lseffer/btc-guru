from config import create_influxdb_dataframe_client
from typing import Dict
from pandas import DataFrame


class InfluxdbQuery():

    query_string = 'SELECT {fields} FROM {measurement} WHERE "asset"=\'{asset}\' ORDER BY time DESC LIMIT {limit}'

    def __init__(self, request_parameters: Dict = {}, result_limit=10000) -> None:
        self.request_parameters = request_parameters
        self.measurement = request_parameters.get('measurement', 'ohlcv')
        self.fields: str = ','.join(request_parameters.get('fields', '*').split(','))
        self.asset = request_parameters.get('asset', 'btc')
        self.result_limit = result_limit

    def _transform_dataframe(self, dataframe: DataFrame) -> DataFrame:
        dataframe_result = dataframe.reset_index() \
            .rename(columns={'index': 'time'})
        return dataframe_result

    def query(self) -> DataFrame:
        influxdb_client = create_influxdb_dataframe_client()
        result_df: DataFrame = influxdb_client.query(self.query_string.format(
            fields=self.fields,
            measurement=self.measurement,
            asset=self.asset,
            limit=self.result_limit
        )).get(self.measurement)
        if result_df is not None:
            result_df = self._transform_dataframe(result_df)
            return result_df
        else:
            return DataFrame()
