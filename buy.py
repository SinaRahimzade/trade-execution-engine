from execution_engine.mofid import MofidBroker
from execution_engine.trackers import tse
from execution_engine.trackers.models import AbstractTracker


class Tracker:
    def __init__(self, ticker: str, broker: MofidBroker):
        self.ticker = ticker
        self.broker = broker
        self.ticker_tracker = tse.TseTickerTracker(ticker)

    def get_ticker_info(self) -> tse.RealtimeTickerInfo:
        return self.ticker_tracker.get_ticker_info()

    def get_inventory(self) -> int:
        self.broker.portfolio()[self.ticker]["quantity"]

    def get_time(self) -> int:
        return 0

    def get_tracker(self):
        return None


def __main__():
    user = "09123152886"
    password = "14@15Dali110"
    broker = MofidBroker(user, password)
    tracker = Tracker("ولغدر", broker)


if __name__ == "__main__":
    __main__()
