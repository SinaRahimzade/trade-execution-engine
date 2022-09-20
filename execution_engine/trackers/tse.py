import datetime
from typing import Dict, List, Tuple

from pytse_client import symbols_data

from execution_engine.config import TSE_ISNT_INFO_URL
from execution_engine.trackers.models import (AbstractTickerTracker, Order,
                                              RealtimeTickerInfo, TradeSummary)
from execution_engine.utils.request_session import requests_retry_session


def get_orders(orders_raw_text: str) -> Tuple[List[Order], List[Order]]:
    if not orders_raw_text:
        return [], []
    buy_orders_set = []
    sell_orders_set = []
    orders = orders_raw_text.split(",")
    orders.pop()  # last item is empty string
    for order_text in orders:
        order_numbers = order_text.split("@")
        buy_orders_set.append(
            Order(
                order_numbers[0],  # count
                order_numbers[1],  # vol
                order_numbers[2],  # price
            )
        )
        sell_orders_set.append(
            Order(
                order_numbers[5],  # count
                order_numbers[4],  # vol
                order_numbers[3],  # price
            )
        )
    return buy_orders_set, sell_orders_set


def get_individual_trade_summary(
    individual_trade_summary_section,
) -> TradeSummary:
    splitted_fields = individual_trade_summary_section.split(",")
    if len(splitted_fields) < 9:
        return None

    individual_buy_vol = float(splitted_fields[0])
    individual_sell_vol = float(splitted_fields[3])
    individual_buy_count = float(splitted_fields[5])
    individual_sell_count = float(splitted_fields[8])

    return TradeSummary(
        buy_vol=individual_buy_vol,
        buy_count=individual_buy_count,
        sell_vol=individual_sell_vol,
        sell_count=individual_sell_count,
    )


def get_corporate_trade_summary(corporate_trade_summary_section):
    splitted_fields = corporate_trade_summary_section.split(",")
    if len(splitted_fields) < 9:
        return None

    corporate_buy_vol = float(splitted_fields[1])
    corporate_sell_vol = float(splitted_fields[4])
    corporate_buy_count = float(splitted_fields[6])
    corporate_sell_count = float(splitted_fields[9])

    return TradeSummary(
        buy_vol=corporate_buy_vol,
        buy_count=corporate_buy_count,
        sell_vol=corporate_sell_vol,
        sell_count=corporate_sell_count,
    )


class TseTickerTracker(AbstractTickerTracker): 
    def __init__(self, ticker: str):
        super().__init__(ticker) 
        self.ticker = ticker 
        self._index = symbols_data.get_ticker_index(ticker) 
        self._info_url = TSE_ISNT_INFO_URL.format(self._index) 
        self.symbol = ticker

    def get_ticker_info(self) -> RealtimeTickerInfo:
        """
        notes on usage:
        - Real time data might not be always available
        check for None values before usage
        """
        if not self.__is_active():
            raise RuntimeError(
                f"Cannot get realtime data from inactive ticker {self.symbol}"
            )
        session = requests_retry_session()
        response = session.get(self._info_url, timeout=5)
        session.close()

        response_sections_list = response.text.split(";")

        if len(response_sections_list) >= 1:
            price_section = response_sections_list[0].split(",")
            try:
                state = self._instrument_state(price_section[1])
                yesterday_price = int(price_section[5])
                open_price = int(price_section[4])
                high_price = int(price_section[6])
                low_price = int(price_section[7])
                count = int(price_section[8])
                volume = int(price_section[9])
                value = int(price_section[10])
                last_date = datetime.datetime.strptime(
                    price_section[12] + price_section[13], "%Y%m%d%H%M%S"
                )
            except (ValueError, IndexError):
                state = None
                yesterday_price = None
                open_price = None
                high_price = None
                low_price = None
                count = None
                volume = None
                value = None
                last_date = None

            # in some cases last price or adj price is undefined
            try:
                last_price = int(price_section[2])
            # when instead of number value is `F`
            except (ValueError, IndexError):
                last_price = None
            try:
                adj_close = int(price_section[3])
            except (ValueError, IndexError):
                adj_close = None

        try:
            info_section = response_sections_list[0].split(",")
            nav = int(info_section[15])
            nav_date = str(info_section[14])
        except (ValueError, IndexError):
            nav = None
            nav_date = None

        try:
            orders_section = response_sections_list[2]
            buy_orders, sell_orders = get_orders(orders_section)
            best_demand_vol = (
                buy_orders[0].volume if 0 < len(buy_orders) else None
            )
            best_demand_price = (
                buy_orders[0].price if 0 < len(buy_orders) else None
            )
            best_supply_vol = (
                sell_orders[0].volume if 0 < len(sell_orders) else None
            )
            best_supply_price = (
                sell_orders[0].price if 0 < len(sell_orders) else None
            )
        except (IndexError):
            buy_orders = []
            sell_orders = []
            best_demand_vol = None
            best_demand_price = None
            best_supply_vol = None
            best_supply_price = None
            buy_orders = None
            sell_orders = None

        if len(response_sections_list) >= 4:
            trade_summary_section = response_sections_list[4]
            individual_trade_summary = get_individual_trade_summary(
                trade_summary_section
            )
            corporate_trade_summary = get_corporate_trade_summary(
                trade_summary_section
            )
        else:

            individual_trade_summary = None
            corporate_trade_summary = None

        return RealtimeTickerInfo(
            state,
            last_price,
            adj_close,
            yesterday_price,
            open_price,
            high_price,
            low_price,
            count,
            volume,
            value,
            last_date,
            best_demand_vol=best_demand_vol,
            best_demand_price=best_demand_price,
            best_supply_vol=best_supply_vol,
            best_supply_price=best_supply_price,
            buy_orders=buy_orders,
            sell_orders=sell_orders,
            individual_trade_summary=individual_trade_summary,
            corporate_trade_summary=corporate_trade_summary,
            nav=nav,
            market_cap=None,
            nav_date=nav_date,
        )

    def __is_active(self):
        """
        Check if ticker is in active state so new data comes in.
        Deactivated symbols have message
        نماد قدیمی حذف شده
        in their name.
        Returns: True if the symbol is in active state
        """
        most_recent_index = symbols_data.get_ticker_index(self.symbol)
        old_indexes = symbols_data.get_ticker_old_index(self.symbol)
        return most_recent_index not in old_indexes

    def _instrument_state(self, state_code) -> str:
        states = {
            "I ": "ممنوع",
            "A ": "مجاز",
            "AG": "مجاز-مسدود",
            "AS": "مجاز-متوقف",
            "AR": "مجاز-محفوظ",
            "IG": "ممنوع-مسدود",
            "IS": "ممنوع-متوقف",
            "IR": "ممنوع-محفوظ",
        }
        return states.get(state_code, "")

        


    