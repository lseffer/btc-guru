from etl import ETL
from config import create_influxdb_client, logger
from helpers import grouper
from typing import Collection


class InfluxdbETL(ETL):

    def __init__(self):
        self.influxdb_client = create_influxdb_client()

    def load(self, iterable: Collection, batch_size=10000) -> None:
        written_rows_count = 0
        influxdb_records = []
        for index, batch in enumerate(grouper(iterable, batch_size)):
            for record in batch:
                if record:
                    influxdb_records.append(record)
            self.influxdb_client.write_points(influxdb_records)
            written_rows_count += len(influxdb_records)
            influxdb_records = []
            logger.info('InfluxDB load: {}/{} records written'.format(written_rows_count,
                                                                      len(iterable)))
