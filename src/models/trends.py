from src.api.client import Client
from src.api.streamtools import AssetObservator
import numpy as np
import psutil
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep
from matplotlib.animation import FuncAnimation
from src.api.commands import get_historical_candles


class MovingAVG():

    def __init__(self, symbol:str,period:int=1) -> None:
        self.api = Client('DEMO')
        self.symbol = symbol
        self.period = period
        self.base_data = None
        self.means = np.empty(shape=[0, 5])
        self.mean = np.empty(shape=[0, 5])
        self.last_1M_candle = np.empty(shape=[1, 6])
        self.signal = None

    
    def get_means(self):
        avg_60_min = np.mean(self.base_data[-60, 2])
        avg_15_min = np.mean(self.base_data[-15, 2])
        avg_5_min = np.mean(self.base_data[-5, 2])
        data = np.array([self.base_data[-1, 0], self.base_data[-1, 2], avg_60_min, avg_15_min, avg_5_min])
        self.means = np.vstack([self.means, data])
        self.mean = data


    def market_observe(self, symbol_data):

        while symbol_data.symbols_last_1M.shape==(0, 7):
            sleep(1)

        while self.api.connection_stream == True:
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
        self.api.open_session()
        self.base_data = get_historical_candles(api=self.api,symbol=self.symbol, shift=60, period=self.period)
        read_thread = Thread(target=self.market_observe, args=(symbol_data,))
        read_thread.start()
        # read_thread.join()


