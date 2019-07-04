import pandas as pd
from config import create_influxdb_client, grouper, logger

# {"ts":1325379600000,"open":4.58,"high":4.58,"low":4.58,"close":4.58,"volume":3.5469090909}


def read_historical_data():
    return pd.read_csv('http://www.cryptodatadownload.com/cdd/gemini_BTCUSD_1hr.csv', skiprows=1)


def create_influxdb_record(historical_data_record):
    json_body = {
        "measurement": "ohlcv",
        "tags": {
            "asset": "btc"
        },
        "time": historical_data_record["Date"],
        "fields": {
            "open": historical_data_record["Open"],
            "high": historical_data_record["High"],
            "low": historical_data_record["Low"],
            "close": historical_data_record["Close"],
            "volume": historical_data_record["Volume"]
        }
    }
    return json_body


if __name__ == '__main__':
    influxdb_client = create_influxdb_client()
    historical_data = read_historical_data()
    batch_size = 10000
    written_rows_count = 0
    influxdb_records = []
    for index, batch in enumerate(grouper(historical_data.iterrows(), batch_size)):
        for row_object in batch:
            if row_object:
                influxdb_record = create_influxdb_record(row_object[1])
                influxdb_records.append(influxdb_record)
        influxdb_client.write_points(influxdb_records)
        written_rows_count += len(influxdb_records)
        influxdb_records = []
        logger.info('Initializing database: {}/{} records written'.format(written_rows_count,
                                                                          len(historical_data)))
