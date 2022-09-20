import math
from typing import final

import numpy as np

from execution_engine.trackers.models import (
    AbstractAcquisition,
    AbstractTracker,
    SendingOrder,
)


class Ghasem(AbstractAcquisition):
    def __init__(
        self,
        tikcer: str,
        final_inventory: int,
        time_step: int,
        expiry: int,
        buy_threshold: float,
    ):
        super().__init__(tikcer, final_inventory, time_step, expiry)
        self.buy_threshold = buy_threshold
        self.final_inventory = final_inventory

    def get_order(self, info: AbstractTracker) -> SendingOrder:
        inventory = info.get_inventory()
        if inventory > self.final_inventory:
            pass
        elif inventory < self.final_inventory and self.buy_condition(info):
            min_quant = max(
                int(int(info.get_ticker_info().sell_orders[0].volume) * 0.5),
                self.final_inventory - inventory,
            )
            return SendingOrder(info.get_ticker_info().best_supply_price, min_quant)

    def buy_condition(self, info: AbstractTracker) -> bool:
        print(
            (
                float(info.get_ticker_info().best_supply_price)
                - float(info.get_ticker_info().yesterday_price)
            )
            / float(info.get_ticker_info().yesterday_price)
        )
        return (
            float(info.get_ticker_info().best_supply_price)
            - float(info.get_ticker_info().yesterday_price)
        ) / float(info.get_ticker_info().yesterday_price) < self.buy_threshold
