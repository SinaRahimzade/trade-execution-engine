import asyncio
import datetime
from collections import namedtuple
from dataclasses import dataclass
from time import time
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
            return self
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

    def _urls(self):
        return [self.TRADE_URL.format(ticker_id) for ticker_id in self.tickers_id]

    async def get_info(sefl, url: str, session: ClientSession):
        async with session.get(url) as response:
            return await response.text()

    async def _get_all_info(self):
        urls = self._urls()
        async with ClientSession() as session:
            tasks = [self.get_info(url, session) for url in urls]
            return await asyncio.gather(*tasks)

    # FIX IT Later, Make it awaitble
    async def _parse_trade_details(self, content):

        soup = bs4.BeautifulSoup(content, "lxml")
        xml_rows = soup.find_all("row")
        rows = []
        for xml_row in xml_rows:
            cells = xml_row.find_all("cell")
            row = [
                datetime.time.fromisoformat(cells[1].text),
                int(cells[2].text),
                float(cells[3].text),
            ]
            rows.append(Tick(*row))
        return rows

    def get_all_info(self):
        return asyncio.run(self._get_all_info())


with open("sample.xml", "w") as f:
    data = MarketWatch(["شپنا"]).get_all_info()[0]
    f.write(data)
