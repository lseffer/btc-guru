from influxdb import InfluxDBClient
from itertools import zip_longest
import os
import logging
import sys

HOME = os.getenv('HOME')
INFLUXDB_USER = os.getenv('INFLUXDB_USER')
INFLUXDB_USER_PASSWORD = os.getenv('INFLUXDB_USER_PASSWORD')
COINAPI_KEY = os.getenv('COINAPI_KEY')


def create_influxdb_client():
    return InfluxDBClient('database', 8086, INFLUXDB_USER, INFLUXDB_USER_PASSWORD, 'crypto')


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    log = logging.getLogger()
    log.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(level)
    log.addHandler(stdout_handler)

    return log


logger = setup_logging(logging.INFO)
