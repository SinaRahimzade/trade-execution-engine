from datetime import datetime
from time import sleep
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
from execution_engine.trackers.tse import TseMultipleTickerTracker


# You can generate an API token from the "API Tokens Tab" in the UI
token = "7VqIFiNN5RmJX9_CmaNiCo5jKTGkC0dchJIv0MSiJi7jwTN3Ziw89T0i2JmtX9uvBl91Ehy4i0f0oUk9k8GZPQ=="
org = "delta"
bucket = "test"


class DataBase:
    token = "7VqIFiNN5RmJX9_CmaNiCo5jKTGkC0dchJIv0MSiJi7jwTN3Ziw89T0i2JmtX9uvBl91Ehy4i0f0oUk9k8GZPQ=="
    org = "delta"
    bucket = "test"
    client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
    write_api = client.write_api(write_options=ASYNCHRONOUS)


def updater(tracker):
    while True:
        try:
            data = tracker.get_info()
        except Exception as e:
            print(e)
            continue
        print("download")
        for info in data:
            try:
                DataBase.write_api.write(
                    bucket=DataBase.bucket, record=info.to_line_protocol()
                )
                print("write")
            except:
                print(info.to_line_protocol())
        print("_________________________________")


updater(TseMultipleTickerTracker())
