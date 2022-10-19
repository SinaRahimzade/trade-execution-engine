from pytse_client import symbols_data
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Optional
import plotly.graph_objs as go
import pandas as pd
import datetime
import time


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
    sector: Optional[str] = None
    symbol: Optional[str] = None

    def to_line_protocol(self):
        return f"ticker_info,symbol={self.symbol},sector={self.sector} last_price={self.last_price},adj_close={self.adj_close},volume={self.volume},value={self.value},best_demand_vol={self.best_demand_vol},best_demand_price={self.best_demand_price},best_supply_vol={self.best_supply_vol},best_supply_price={self.best_supply_price}"

    def set_supply_demand(self, orders: List[Order]):
        self.best_supply_vol = orders[1].volume
        self.best_supply_price = orders[1].price
        self.best_demand_vol = orders[0].volume
        self.best_demand_price = orders[0].price


@dataclass
class Tracker:
    ticker_info: RealtimeTickerInfo
    inventory: int
    time: int


@dataclass
class Asset:
    quantity: int
    isin: str
    total_quantity_buy: int
    total_quantity_sell: int
    new_buy: int
    new_sell: int
    last_trade_price: float
    price_var: float
    first_symbol_state: str
    symbol: str
    market_unit: str
    asset_id: str


class AbstractTracker(ABC):
    def __init__(self, ticker: str):
        self.ticker = ticker

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
        self, ticker: str, initial_inventory: int, time_step: int, expiry: int
    ):
        self.ticker = ticker
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

    def __init__(self, ticker: str, final_inventory: int, time_step: int, expiry: int):
        self.ticker = ticker
        self.isin = symbols_data.symbols_information()[ticker]["code"]
        self.initial_deposit = final_inventory
        self.time_step = time_step
        self.expiry = expiry

    @abstractmethod
    def get_order(self, info: AbstractTracker) -> SendingOrder:
        pass

    def run(self, tracker, oms):
        while True:
            order = self.get_order(tracker)
            if order is not None:
                self.send_order(order, oms)
            time.sleep(self.time_step)

    def send_order(self, order: SendingOrder, oms):
        oms.send_order(
            order_type=self.SIDE,
            ticker_isin_code=self.isin,
            quantity=order.count,
            price=order.price,
        )


class AbstractAlgorithms(ABC):

    def __init__(self, ticker: str, time_step: int):

        self.ticker = ticker
        self.time_step = time_step

    @abstractmethod
    def generate_signal(self):
        pass

    @abstractmethod
    def get_intraday_data(self):
        pass

    @abstractmethod
    def get_daily_data(self):
        pass

    @abstractmethod
    def visualize_signals(self, timeframe: str):

        dataframe = None

        if timeframe.lower() == 'daily':
            dataframe = self.get_daily_data()
        elif timeframe.lower() == 'intraday':
            dataframe = self.get_intraday_data()

        dataframe.reset_index(inplace=True)
        signals_array = pd.DataFrame(self.generate_signal())
        signals_array['date'] = pd.DatetimeIndex(signals_array['date'])
        dataframe = dataframe.merge(pd.DataFrame(self.generate_signal()), on='date')
        dataframe.set_index('date', inplace=True)

        buying_events = dataframe.loc[dataframe['signal'] == 1].index.to_list()
        selling_events = dataframe.loc[dataframe['signal'] == -1].index.to_list()

        figure = go.Figure()

        figure.add_trace(go.Scatter(x=dataframe.index, y=dataframe['adjClose'].values, name='adjClose',
                                    line=dict(color='#000000', width=1)))

        figure.add_trace(go.Scatter(x=buying_events, y=dataframe['adjClose'].loc[buying_events].values,
                                    name='Buying Events', mode='markers',
                                    marker=dict(color='#00FF00', size=8, symbol='triangle-up')))

        figure.add_trace(go.Scatter(x=selling_events, y=dataframe['adjClose'].loc[selling_events].values,
                                    name='Selling Events', mode='markers',
                                    marker=dict(color='#FF0000', size=8, symbol='triangle-down')))

        figure.update_layout(title_text='Signals', xaxis_title='Date', yaxis_title='Price')

        figure.write_html(f'{self.ticker}.html', auto_open=True)


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
