from api.client import Client
from api.streamtools import AssetObservator
import numpy as np
import psutil
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep


class MovingAVG():

    def __init__(self,api:Client,symbol:str,period:int=1) -> None:
        self.api = api
        self.symbol = symbol
        self.period = period
        self.base_data = None
        self.means = np.empty(shape=[0, 5])
        self.mean = np.empty(shape=[0, 5])
        self.observator = AssetObservator(api=api,symbol=self.symbol,period=period)
        self.signal = None

    
    def get_means(self):
        avg_60_min = np.mean(self.base_data[-60, 2])
        avg_15_min = np.mean(self.base_data[-15, 2])
        avg_5_min = np.mean(self.base_data[-5, 2])
        data = np.array([self.base_data[-1, 0], self.base_data[-1, 2], avg_60_min, avg_15_min, avg_5_min])
        self.means = np.vstack([self.means, data])
        self.mean = data


    def data_stream(self):
        self.observator.subscribe()
        while self.api.connection_stream == True:
                self.base_data = self.observator.base_data
                self.get_means()
                if self.mean[1] > self.mean[3]:
                    self.signal = 0
                if self.mean[1] < self.mean[3]:
                    self.signal = 1
                self.observator.streamread()


    def run(self):
        read_thread = Thread(target=self.data_stream, args=())
        read_thread.start()



    def data_plot(self):
        # plt.rcParams['animation.html'] = 'jshtml'
        # fig = plt.figure()
        
        # while self.api.connection_stream == True:
        #     x = self.means[:,0]
        #     price = self.means[:,1]
        #     mean_5 = self.means[:,2]
        #     mean_15 = self.means[:,3]
        #     mean_60 = self.means[:,4]
        #     plt.plot(x, price, label='close')
        #     plt.plot(x, mean_5, label='mean M5')
        #     plt.plot(x, mean_15, label='mean M15')
        #     plt.plot(x, mean_60, label='mean H1')
        #     plt.legend(loc='upper left')

        # plt.show()
        
        
        fig = plt.figure()
        x, price, mean_5, mean_15, mean_60 = [], [], [], [], []

        while True:
            x.append(self.means[-1,0])
            price.append(self.means[-1,1])
            mean_5.append(self.means[-1,2])
            mean_15.append(self.means[-1,3])
            mean_60.append(self.means[-1,4])

            plt.plot(x, price, label='close')
            plt.plot(x, mean_5, label='mean M5')
            plt.plot(x, mean_15, label='mean M15')
            plt.plot(x, mean_60, label='mean H1')

            # fig.canvas.draw()

            # ax.set_xlim(left=max(0, x[-1] - 50), right=x[-1] + 50)
        
            plt.show(block=False)
            plt.legend(loc='upper left')
            plt.pause(1)



















        
