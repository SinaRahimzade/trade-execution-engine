from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# You can generate an API token from the "API Tokens Tab" in the UI
token = "7VqIFiNN5RmJX9_CmaNiCo5jKTGkC0dchJIv0MSiJi7jwTN3Ziw89T0i2JmtX9uvBl91Ehy4i0f0oUk9k8GZPQ=="
org = "delta"
bucket = "stocks"



class DataBase:
    def __init__(self, token: str, org: str, bucket: str):
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)

    def update(self,symbol: str, point: str, value: str):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        p = Point(point).tag("symbol", symbol).field("value", value)
        write_api.write(bucket=self.bucket, record=p)
        write_api.close()
        