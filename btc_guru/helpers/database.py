from config import create_influxdb_dataframe_client
from typing import Dict
from pandas import DataFrame


class InfluxdbApiQuery():

    query_string = 'SELECT {fields} FROM {measurement} WHERE "asset"=\'{asset}\' ORDER BY time DESC LIMIT 10000'

    def __init__(self, request_parameters: Dict) -> None:
        self.request_parameters = request_parameters
        self.measurement = request_parameters.get('measurement', 'ohlcv')
        self.fields: str = ','.join(request_parameters.get('fields', '*').split(','))
        self.asset = request_parameters.get('asset', 'btc')

    def _create_influxdb_client(self) -> None:
        self.influxdb_client = create_influxdb_dataframe_client()

    def _transform_dataframe(self, dataframe: DataFrame) -> DataFrame:
        dataframe_result = dataframe.reset_index() \
            .rename(columns={'index': 'time'})
        return dataframe_result

    def query(self) -> str:
        self._create_influxdb_client()
        result_df: DataFrame = self.influxdb_client.query(self.query_string.format(
            fields=self.fields,
            measurement=self.measurement,
            asset=self.asset
        )).get(self.measurement)
        if result_df is not None:
            result_df = self._transform_dataframe(result_df)
            return result_df.to_json(orient='split', index=False)
        else:
            return "No data returned, check your query parameters"
