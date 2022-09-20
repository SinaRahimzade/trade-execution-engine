import datetime
import time
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Optional

from pytse_client import symbols_data

from execution_engine.brokers import MofidBroker


@dataclass
class TradeSummary:
    buy_vol: float
    buy_count: float
    sell_vol: float
    sell_count: float


Order = namedtuple("order", ["count", "volume", "price"])

SendingOrder = namedtuple("sending_order", ["count", "price"])


@dataclass
class RealtimeTickerInfo:
    state: Optional[str]
    last_price: Optional[float]
    adj_close: Optional[float]
    yesterday_price: Optional[float]
    open_price: Optional[float]
    high_price: Optional[float]
    low_price: Optional[float]
    count: Optional[int]
    volume: Optional[int]
    value: Optional[int]
    last_date: Optional[datetime.datetime]
    best_demand_vol: Optional[int]
    best_demand_price: Optional[float]
    best_supply_vol: Optional[int]
    best_supply_price: Optional[float]
    sell_orders: Optional[List[Order]]
    buy_orders: Optional[List[Order]]
    individual_trade_summary: Optional[TradeSummary]
    corporate_trade_summary: Optional[TradeSummary]
    nav: Optional[int]
    nav_date: Optional[str]
    # ارزش بازار
    market_cap: Optional[int]


@dataclass
class Tracker:
    ticker_info: RealtimeTickerInfo
    inventory: int
    time: int


class AbstractTracker(ABC):
    def __init__(self, tikcer: str):
        self.ticker = tikcer

    @abstractmethod
    def get_ticker_info(self) -> RealtimeTickerInfo:
        pass

    @abstractmethod
    def get_inventory(self) -> int:
        pass

    @abstractmethod
    def get_time(self) -> int:
        pass

    @abstractmethod
    def get_tracker(self) -> Tracker:
        pass


class AbstractLiquidation(ABC):
    def __init__(
        self, tikcer: str, initial_inventory: int, time_step: int, expiry: int
    ):
        self.ticker = tikcer
        self.initial_deposit = initial_inventory
        self.time_step = time_step
        self.expiry = expiry

    @abstractmethod
    def get_order(self, info: AbstractTracker) -> SendingOrder:
        pass

    def send_order(self, order: SendingOrder):
        pass


class AbstractAcquisition(ABC):
    SIDE = 0

    def __init__(self, tikcer: str, final_inventory: int, time_step: int, expiry: int):
        self.ticker = tikcer
        self.isin = symbols_data.symbols_information()[tikcer]["code"]
        self.initial_deposit = final_inventory
        self.time_step = time_step
        self.expiry = expiry

    @abstractmethod
    def get_order(self, info: AbstractTracker) -> SendingOrder:
        pass

    def run(self, tracker, oms):
        while True:
            order = self.get_order(tracker)
            self.send_order(order, oms)
            time.sleep(self.time_step)

    def send_order(self, order: SendingOrder, oms):
        oms.send_order(
            self.SIDE,
            self.isin,
            order.count,
            order.price,
        )


class AbstractOms(ABC):
    @abstractmethod
    def send_sell_order(self, order: SendingOrder) -> bool:
        pass

    @abstractmethod
    def send_buy_order(self, order: SendingOrder) -> bool:
        pass

    @abstractmethod
    def get_inventory(self, ticker: str) -> int:
        pass

    @abstractmethod
    def get_total_money(self) -> int:
        pass


class AbstractTickerTracker(ABC):
    def __init__(self, ticker: str):
        self.ticker = ticker

    @abstractmethod
    def get_ticker_info(self) -> RealtimeTickerInfo:
        pass
