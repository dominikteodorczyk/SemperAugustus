from api.client import Client
from api.streamtools import AssetObservator
import numpy as np
import psutil
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep
from matplotlib.animation import FuncAnimation
from api.commands import get_historical_candles


class MovingAVG():

    def __init__(self,api:Client,symbol:str,period:int=1) -> None:
        self.api = api
        self.symbol = symbol
        self.period = period
        self.base_data = get_historical_candles(api=api,symbol=self.symbol, shift=60, period=period)
        self.means = np.empty(shape=[0, 5])
        self.mean = np.empty(shape=[0, 5])
        self.signal = None

    
    def get_means(self):
        avg_60_min = np.mean(self.base_data[-60, 2])
        avg_15_min = np.mean(self.base_data[-15, 2])
        avg_5_min = np.mean(self.base_data[-5, 2])
        data = np.array([self.base_data[-1, 0], self.base_data[-1, 2], avg_60_min, avg_15_min, avg_5_min])
        self.means = np.vstack([self.means, data])
        self.mean = data


    def market_observe(self, symbol_data):
        pass
        # while self.api.connection_stream == True:
            #TODO: przypisywanie aktualnej wartosci aktywów i bierzących candles jeśli są nowe
            # if symbol_data.
            #     self.get_means()
            #     print(self.mean)
            #     if self.mean[1] > self.mean[3]:
            #         self.signal = 0
            #     if self.mean[1] < self.mean[3]:
            #         self.signal = 1


                


    def run(self):
        read_thread = Thread(target=self.data_stream, args=())
        read_thread.start()
        # read_thread.join()


