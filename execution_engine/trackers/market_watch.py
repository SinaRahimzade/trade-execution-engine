import asyncio
import datetime
from collections import namedtuple
from dataclasses import dataclass
from typing import List

import bs4
import pandas as pd
import requests
from aiohttp import ClientSession
from pytse_client import symbols_data

Ohlcv = namedtuple("ohlcv", ["open", "high", "low", "close", "volume", "date"])


class MarketWatch:
    TRADE_URL = "http://www.tsetmc.com/tsev2/data/TradeDetail.aspx?i={}"

    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.tickers_id = [symbols_data.get_ticker_index(symbol) for symbol in symbols]

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
            rows.append(row)
        return pd.DataFrame(rows, columns=["date", "volume", "price"])

    def get_all_info(self):
        return asyncio.run(self._get_all_info())


with open("sample.xml", "w") as f:
    data = MarketWatch(["شپنا"]).get_all_info()[0]
    f.write(data)
