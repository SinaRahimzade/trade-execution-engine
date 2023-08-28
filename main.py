from execution_engine.trackers.models import AbstractTracker
from execution_engine.algos import almen_chris, ghasem
from execution_engine.mofid import MofidBroker
from execution_engine.trackers import tse
from pytse_client import symbols_data
from time import sleep


class TestTracker(AbstractTracker):
    def __init__(self, ticker: str):
        AbstractTracker.__init__(self, ticker)
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
    @staticmethod
    def send_order(order_type, isin, quant, price):
        print(f"Sending order: {order_type}, {isin}, {quant}, {price}")
