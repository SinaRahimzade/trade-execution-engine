import math

import numpy as np

from execution_engine.trackers.models import (
    AbstractAcquisition,
    AbstractTracker,
    SendingOrder,
)


class AlmenChris(AbstractAcquisition):
    def __init__(
        self,
        final_inventory: int,
        time_step: float,
        expiry: float,
        alpha: float,
        b: float,
        k: float,
        phi: float,
    ):
        self.expiry = expiry
        self.time_step = time_step
        self.final_inventory = final_inventory
        self.alpha = alpha
        self.b = b
        self.k = k
        self.phi = phi
        self.gamma = (phi / k) ** (0.5)
        self.xi = (alpha + 0.5 * b + (k * phi) ** 0.5) / (
            alpha + 0.5 * b - (k * phi) ** 0.5
        )
        self._t = self.compute_t()

    def compute_t(self) -> np.ndarray:
        return np.arange(0, self.expiry, self.time_step)

    def optimal_inventory(self):
        up = (self.xi * (math.e ** (self.gamma * (self.expiry - self._t)))) - (
            math.e ** (-self.gamma * (self.expiry - self._t))
        )
        down = (self.xi * (math.e ** (self.gamma * self.expiry))) - (
            math.e ** (-self.gamma * self.expiry)
        )
        return np.divide(up, down) * self.final_inventory

    def get_order(self, info: AbstractTracker) -> SendingOrder:
        inventory = info.get_inventory()
        time = info.get_time()
        optimal_inventory = self.optimal_inventory()[time]
        if inventory > optimal_inventory:
            pass
        elif inventory < optimal_inventory:
            return SendingOrder(
                info.get_ticker_info().best_supply_price,
                self.final_inventory - inventory,
            )
