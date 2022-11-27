import asyncio
import datetime
from collections import namedtuple
from dataclasses import dataclass
from time import time
from time import sleep
from typing import List

import bs4
import pandas as pd
import requests
from aiohttp import ClientSession
from pytse_client import symbols_data

from execution_engine.utils.time_utils import time_ceil, time_floor

Tick = namedtuple("Tick", ["time", "volume", "price"])


@dataclass
class LastCandle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    date: datetime.datetime

    def __post_init__(self):
        self.start_date = time_floor(self.date, 1)
        self.end_date = time_ceil(self.date, 1)
        self.status = "open"

    def update(self, tick: namedtuple):
        if tick.time < self.start_date:
            raise ValueError(
                "Tick time is before candle start time, make sure you are using sorted ticks"
            )
        if tick.time > self.end_date:
            self.status = "closed"

        self.high = max(self.high, tick.price)
        self.low = min(self.low, tick.price)
        self.close = tick.price
        self.volume += tick.volume


class MarketWatch:
    TRADE_URL = "http://www.tsetmc.com/tsev2/data/TradeDetail.aspx?i={}"

    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.tickers_id = [symbols_data.get_ticker_index(symbol) for symbol in symbols]
        self.trade_counts_buffer = dict(zip(self.symbols, [0] * len(self.symbols)))
        self.last_candles = dict(zip(self.symbols, [None] * len(self.symbols)))
        self.bars = dict(zip(self.symbols, [None] * len(self.symbols)))
        self.initialize()

    def _urls(self):
        return [self.TRADE_URL.format(ticker_id) for ticker_id in self.tickers_id]

    def get_info_sync(self, url):
        return requests.get(url).content

    async def get_info(sefl, url: str, session: ClientSession):
        async with session.get(url) as response:
            return await response.text()

    async def _get_all_info(self):
        urls = self._urls()
        async with ClientSession() as session:
            tasks = [self.get_info(url, session) for url in urls]
            return await asyncio.gather(*tasks)

    def _parse_trade_details(self, content):
        soup = bs4.BeautifulSoup(content, "lxml")
        xml_rows = soup.find_all("row")
        rows = []
        for xml_row in xml_rows:
            cells = xml_row.find_all("cell")
            time = datetime.time.fromisoformat(cells[1].text)
            date = datetime.datetime.now().date()
            time = datetime.datetime.combine(date, time)
            row = [
                time,
                int(cells[2].text),
                float(cells[3].text),
            ]
            rows.append(Tick(*row))
        return rows

    def update(self, symbol: str, tick: namedtuple):
        if self.last_candles[symbol] is None:
            self.last_candles[symbol] = LastCandle(
                open=tick.price,
                high=tick.price,
                low=tick.price,
                close=tick.price,
                volume=tick.volume,
                date=tick.time,
            )
        else:
            self.last_candles[symbol].update(tick)
            if self.last_candles[symbol].status == "closed":
                if self.bars[symbol] is None:
                    self.bars[symbol] = pd.DataFrame(
                        [
                            {
                                "open": self.last_candles[symbol].open,
                                "high": self.last_candles[symbol].high,
                                "low": self.last_candles[symbol].low,
                                "close": self.last_candles[symbol].close,
                                "volume": self.last_candles[symbol].volume,
                                "date": self.last_candles[symbol].start_date,
                            }
                        ]
                    )
                else:
                    self.bars[symbol] = self.bars[symbol].append(
                        {
                            "open": self.last_candles[symbol].open,
                            "high": self.last_candles[symbol].high,
                            "low": self.last_candles[symbol].low,
                            "close": self.last_candles[symbol].close,
                            "volume": self.last_candles[symbol].volume,
                            "date": self.last_candles[symbol].start_date,
                        },
                        ignore_index=True,
                    )
                self.last_candles[symbol] = LastCandle(
                    open=tick.price,
                    high=tick.price,
                    low=tick.price,
                    close=tick.price,
                    volume=tick.volume,
                    date=tick.time,
                )

    def initialize(self):
        for symbol, content in zip(self.symbols, self.get_all_info()):
            ticks = self._parse_trade_details(content)
            for tick in ticks:
                self.update(symbol, tick)
            self.trade_counts_buffer[symbol] = len(ticks)

    def initialize_symbol(self, symbol: str):
        content = self.get_info_sync(self._urls[symbol])
        ticks = self._parse_trade_details(content)
        for tick in ticks:
            self.update(symbol, tick)
        self.trade_counts_buffer[symbol] = len(ticks)

    def run(self):
        while True:
            for symbol, content in zip(self.symbols, self.get_all_info()):
                ticks = self._parse_trade_details(content)
                for tick in ticks[self.trade_counts_buffer[symbol] :]:
                    self.update(symbol, tick)
                self.trade_counts_buffer[symbol] = len(ticks)
            for symbol in self.bars:
                if self.bars[symbol] is not None:
                    self.bars[symbol].to_csv(f"{symbol}.csv")
            sleep(10)

    def get_all_info(self):
        return asyncio.run(self._get_all_info())


with open("sample.xml", "w") as f:
    MarketWatch(["شپنا", "فولاد"]).run()
