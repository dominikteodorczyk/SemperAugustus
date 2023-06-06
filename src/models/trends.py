"""
Module containing models that make decisions based on trend.
"""

from threading import Thread
from time import sleep
import numpy as np
from api.client import Client
from api.commands import get_historical_candles



class MovingAVG():
    """
    Class representing moving average calculations for a given symbol.

    Args:
        symbol (str): The symbol for which Moving Average calculations
            are performed.
        period (int, optional): The period of Moving Average. Defaults
            to 1 (based on 1-minutes candles).

    Attributes:
        client (Client): An instance of the Client class for making API calls.
        symbol (str): The symbol for which Moving Average calculations
            are performed.
        period (int): The period of Moving Average.
        base_data: Placeholder for storing the base data.
        means: Array for storing the calculated moving averages.
        mean: Array for storing the latest moving average.
        last_1M_candle: Array for storing the data of the last 1-minute candle.
        signal: The generated signal based on Moving Average calculations.
    """

    def __init__(self, symbol: str, period: int = 1) -> None:
        self.client = Client("DEMO")
        self.symbol = symbol
        self.period = period
        self.base_data = None
        self.means = np.empty(shape=[0, 5])
        self.mean = np.empty(shape=[0, 5])
        self.last_1M_candle = np.empty(shape=[1, 6])
        self.signal = None

    def get_means(self):
        """
        A method that calculates moving averages.
        """
        avg_60_min = np.mean(self.base_data[-60, 2])
        avg_15_min = np.mean(self.base_data[-15, 2])
        avg_5_min = np.mean(self.base_data[-5, 2])
        data = np.array(
            [
                self.base_data[-1, 0],
                self.base_data[-1, 2],
                avg_60_min,
                avg_15_min,
                avg_5_min,
            ]
        )
        self.means = np.vstack([self.means, data])
        self.mean = data

    def market_observe(self, symbol_data):
        """
        A method that observes market behavior using streamed data.
        """
        while symbol_data.symbols_last_1M.shape == (0, 7):
            sleep(1)

        while self.client.connection_stream is True:
            if self.last_1M_candle[0, 0] == symbol_data.symbols_last_1M[0, 0]:
                pass
            else:
                self.last_1M_candle = symbol_data.symbols_last_1M
                self.base_data = np.vstack([self.base_data, self.last_1M_candle])
                self.base_data = self.base_data[-60:, :]
                try:
                    self.get_means()
                    if self.mean[4] > self.mean[3]:
                        self.signal = 0
                    if self.mean[4] < self.mean[3]:
                        self.signal = 1
                except:
                    pass
            sleep(1)

    def run(self, symbol_data):
        """
        A method that runs the model's work along with downloading historical data.
        """
        self.client.open_session()
        self.base_data = get_historical_candles(
            client=self.client, symbol=self.symbol, shift=60, period=self.period
        )
        read_thread = Thread(target=self.market_observe, args=(symbol_data,))
        read_thread.start()
