from time import sleep

from pytse_client import symbols_data

from execution_engine.algos import almen_chris, ghasem
from execution_engine.mofid import MofidBroker
from execution_engine.trackers import tse
from execution_engine.trackers.models import AbstractTracker


class TestTracker(AbstractTracker):
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.ticker_tracker = tse.TseTickerTracker(ticker)

    def get_ticker_info(self) -> tse.RealtimeTickerInfo:
        return self.ticker_tracker.get_ticker_info()

    def get_inventory(self) -> int:
        return 0

    def get_time(self) -> int:
        return 0

    def get_tracker(self):
        return None


class Oms:
    def send_order(self, type, isin, quant, price):
        print(f"Sending order: {type}, {isin}, {quant}, {price}")


username = "09123152886"
password = "14@15Dali110"
oms = MofidBroker(username=username, password=password)
print(oms.get_portfolio().text)
