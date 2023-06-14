"""
Module containing models for closing positions.
"""

from threading import Thread
from time import sleep
from typing import Any
from api.client import XTBClient
from api.streamtools import PositionObservator
from api.commands import close_position
from utils.technical import setup_logger


class DefaultCloseSignal:
    """
    Class representing the default close signal for a trading position.

    Attributes:
        logging: The logger object for logging close signal information.
        closedata: Placeholder for storing data related to the closed
            position.
        status_to_close (bool): Flag indicating whether the position
            should be closed.
        api: The API object for interacting with the trading platform.
        symbol: The symbol of the trading position.
        order: Placeholder for storing the order related to the position.
        position: Placeholder for storing position-related information.
        open_price: The opening price of the position.
        margin: The margin associated with the position.
        cmd: The command type of the position (buy/sell).
        volume: The volume of the position.
        asymetric_tp: Placeholder for asymmetrical take profit value.
        sl_start: The starting value for the stop-loss.
        tp_min: The minimum value for the take profit.
        tp_max: The maximum value for the take profit.
        price_data: Placeholder for storing price-related data.
        multiplier_value: The multiplier value used in position
            calculations.
        as_bid_position: Placeholder for storing bid-related
            position information.
        cs_function: Placeholder for storing the close signal function.
        not_earnings_stage (bool): Flag indicating whether the position
            is not in the earnings stage.
        yes_earnings_stage (bool): Flag indicating whether the position
            is in the earnings stage.
        acc_earnings_stage_0 (bool): Flag indicating accumulated earnings
            stage 0.
        acc_earnings_stage_05 (bool): Flag indicating accumulated earnings
            stage 0.5.
        acc_earnings_stage_1 (bool): Flag indicating accumulated earnings
            stage 1.
        acc_earnings_stage_5 (bool): Flag indicating accumulated earnings
            stage 5.
        acc_earnings_stage_15 (bool): Flag indicating accumulated earnings
            stage 15.
    """

    def __init__(self):
        self.logging = setup_logger("DCS_logger", "DCS_logger.log")
        self.closedata: dict[str, Any]
        self.status_to_close: bool = False
        self.client: XTBClient
        self.symbol: str
        self.order: int
        self.position: int
        self.open_price: float
        self.margin: float
        self.cmd: int
        self.volume: float
        self.asymetyric_tp: float
        self.sl_start: float
        self.tp_min: float
        self.tp_max: float
        self.price_data: PositionObservator
        self.multiplier_value: int
        self.as_bid_position: int
        self.cs_function = None
        self.not_earnings_stage: bool = True
        self.yes_earnings_stage: bool = False
        self.acc_earnings_stage_0: bool = False
        self.acc_earnings_stage_05: bool = False
        self.acc_earnings_stage_1: bool = False
        self.acc_earnings_stage_5: bool = False
        self.acc_earnings_stage_15: bool = False

    def set_params(
        self,
        client: XTBClient,
        position_data: dict[str, Any],
        sl_start: float = 2.0,
        tp_min: float = 0.5,
        tp_max: float = 0.1,
        asymetyric_tp: float = 0.5,
    ):
        """
        A method that allows you to define the parameters of the model after
        the execution of the transaction .
        """
        self.client = client
        self.order = position_data.get("order_no", 0)
        self.margin = position_data.get("margin", 0)
        self.asymetyric_tp = asymetyric_tp
        self.sl_start = sl_start
        self.tp_min = tp_min
        self.tp_max = tp_max
        if isinstance(position_data.get("transactions_data", 0), dict):
            transaction_data = position_data.get("transactions_data", 0)
            self.symbol = transaction_data.get("symbol", 0)
            self.position = transaction_data.get("position", 0)
            self.open_price = transaction_data.get("open_price", 0)
            self.cmd = transaction_data.get("cmd", 0)
            self.volume = transaction_data.get("volume", 0)
            self.price_data = PositionObservator(
                client=client, symbol=self.symbol, order_no=self.order
            )
        else:
            self.logging.info("Not transactions data")

        if self.cmd == 1:
            self.multiplier_value = 1
            self.as_bid_position = 0
            self.cs_function = self.sell_take_profit_signal
        else:
            self.multiplier_value = -1
            self.as_bid_position = 1
            self.cs_function = self.buy_take_profit_signal

    def subscribe_data(self):
        """
        Data subscription in the position observation object.
        """
        self.price_data.subscribe()

    def read_data(self):
        """
        Reading data from the stream in the position observation object.
        """
        while self.status_to_close is False:
            self.price_data.stream()

    def get_current_percentage(self) -> float:
        """
        Calculation of the current percentage of position return.

        Return:
            Percentage of transaction return (float)
        """
        try:
            return (self.price_data.profit / self.margin) * 100
        except Exception:
            return self.sl_start

    def get_candle_mean(self, cendle_data):
        """
        Calculates the average of the opening and closing price of a candle.

        Return:
            Returns the average between the opening and closing prices.
        """
        mean_prince = (cendle_data[0, 2] - cendle_data[0, 1]) / 2
        return cendle_data[0, 1] + mean_prince

    def control_asset(self):
        """
        Monitoring by position type
        """
        if self.cmd == 0:
            while self.status_to_close is False:
                self.buy_take_profit_signal()
                sleep(0.001)
        if self.cmd == 1:
            while self.status_to_close is False:
                self.sell_take_profit_signal()
                sleep(0.001)

    def calculate_buy_cs(self, candle, current_price):
        """
        Based on the average value of the candle and the current price,
        makes a decision to close the position
        """
        mean_candle_value = self.get_candle_mean(candle)
        if current_price > mean_candle_value:
            pass
        else:
            self.closedata = close_position(
                client=self.client,
                symbol=self.symbol,
                position=self.position,
                volume=self.volume,
                cmd=self.cmd,
            )
            self.status_to_close = True

    def calculate_sell_cs(self, candle, current_price):
        """
        Based on the average value of the candle and the current price,
        makes a decision to close the position
        """
        mean_candle_value = self.get_candle_mean(candle)
        if current_price < mean_candle_value:
            pass
        else:
            self.closedata = close_position(
                client=self.client,
                symbol=self.symbol,
                position=self.position,
                volume=self.volume,
                cmd=self.cmd,
            )
            self.status_to_close = True

    def buy_take_profit_signal(self):
        """
        On the basis of market behavior and recorded data, makes decisions
        to close positions.
        """
        try:
            current_price = self.price_data.curent_price[
                0, self.as_bid_position
            ]
            current_percentage = self.get_current_percentage()
            if current_percentage <= 0:
                if current_percentage > (-1 * self.sl_start):
                    pass
                else:
                    self.closedata = close_position(
                        client=self.client,
                        symbol=self.symbol,
                        position=self.position,
                        volume=self.volume,
                        cmd=self.cmd,
                    )
                    self.status_to_close = True
            if current_percentage > 0:
                if self.price_data.minute_15.any():
                    self.calculate_buy_cs(
                        self.price_data.minute_15, current_price
                    )
                elif self.price_data.minute_5.any():
                    self.calculate_buy_cs(
                        self.price_data.minute_5, current_price
                    )
                elif self.price_data.minute_1.any():
                    # self.calculate_buy_cs
                    # (self.price_data.minute_1,current_price)
                    pass
                elif not self.price_data.minute_1.any():
                    pass
                else:
                    self.logging.info("PASS")
        except Exception:
            pass

    def sell_take_profit_signal(self):
        """
        On the basis of market behavior and recorded data, makes decisions
        to close positions.
        """
        try:
            current_price = self.price_data.curent_price[
                0, self.as_bid_position
            ]
            current_percentage = self.get_current_percentage()
            if current_percentage <= 0:
                if current_percentage > (-1 * self.sl_start):
                    sleep(0.1)
                else:
                    self.closedata = close_position(
                        client=self.client,
                        symbol=self.symbol,
                        position=self.position,
                        volume=self.volume,
                        cmd=self.cmd,
                    )
                    self.status_to_close = True
            if current_percentage > 0:
                if self.price_data.minute_15.any():
                    self.calculate_sell_cs(
                        self.price_data.minute_15, current_price
                    )
                elif self.price_data.minute_5.any():
                    self.calculate_sell_cs(
                        self.price_data.minute_5, current_price
                    )
                elif self.price_data.minute_1.any():
                    # self.calculate_sell_cs
                    # (self.price_data.minute_1,current_price)
                    pass
                elif not self.price_data.minute_1.any():
                    pass
                else:
                    self.logging.info("PASS")
        except Exception:
            pass

    def run(self):
        """
        Launches the model and the thread of observing the market
        and reacting to the data by closing positions.
        """
        self.subscribe_data()
        read_thread = Thread(target=self.read_data, args=())
        control_thread = Thread(target=self.control_asset, args=())

        read_thread.start()
        control_thread.start()

        read_thread.join()
        control_thread.join()
