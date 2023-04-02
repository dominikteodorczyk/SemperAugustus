import json
import numpy as np
from time import time
from utils.setup_loger import setup_logger

class Stream():

    def __init__(self) -> None:
        
        pass

class WalletStream():

    def __init__(self, api=None) -> None:
        self.api = api
        self.balance = None

    def keepalive(self):
        return self.api.stream_send({"command": "getKeepAlive", "streamSessionId": self.api.stream_sesion_id})

    def subscribe(self):
        return self.api.stream_send({"command": "getBalance", "streamSessionId": self.api.stream_sesion_id})

    def streamread(self):
        message = self.api.stream_read()
        try:
            if message['command'] == 'balance':
                self.balance = np.fromiter(message['data'].values(), dtype=float)
        except:
            pass

    def stream(self):
        self.subscribe()
        while self.api.connection_stream == True:
            self.streamread()
            self.keepalive()


class PositionObservator():

    def __init__(self, api=None, symbol=None, order_no = None) -> None:
        self.obs_logger = setup_logger(f'{symbol}-{order_no}','beta\log\obs_logger.log')

        self.api = api
        self.symbol = symbol
        self.order_no = order_no
        self.curent_price = np.empty(shape=[0, 11])
        self.profit = None
        self.minute_1 = np.empty(shape=[0, 7])
        self.minute_5 = np.empty(shape=[0, 7])
        self.minute_15 = np.empty(shape=[0, 7])

        self.minute_1_5box = np.empty(shape=[0, 7])
        self.minute_5_15box = np.empty(shape=[0, 7])


    def keepalive(self):
        return self.api.stream_send({"command": "getKeepAlive", "streamSessionId": self.api.stream_sesion_id})

    def subscribe(self):
        self.api.stream_send(
            {"command": "getCandles",
             "streamSessionId": self.api.stream_sesion_id,
             "symbol": "EURUSD"}
        )
        self.api.stream_send(
            {"command": "getTickPrices",
             "streamSessionId": self.api.stream_sesion_id, 
             "symbol": "EURUSD"}
        )
        self.api.stream_send(
            {"command": "getProfits",
             "streamSessionId": self.api.stream_sesion_id}
        )  

    def streamread(self):
        message = self.api.stream_read()
        if message['command'] == 'candle':
            # 'ctm', 'open', 'close', 'high', 'low', 'vol', 'quoteId'
            dictor=message["data"]
            dictor.pop('ctmString')
            dictor.pop('symbol')
            self.minute_1 = np.fromiter(dictor.values(), dtype=float).reshape(1,7)
            self.minute_1_5box = np.vstack([self.minute_1_5box, self.minute_1])
            self.obs_logger.info(f'1MIN: {self.minute_1.tolist()[0]}')
        if message["command"] == 'tickPrices':
            # 'ask','bid','high','low','askVolume','bidVolume','timestamp','level','quoteId','spreadTable','spreadRaw'
            dictor=message["data"]
            if dictor["symbol"] == self.symbol:
                dictor.pop('symbol')
                self.curent_price = np.fromiter(dictor.values(), dtype=float).reshape(1,11)
                self.obs_logger.info(f'PRICE: {self.curent_price.tolist()[0]}')
        if message["command"] == "profit":
            dictor=message["data"]
            if dictor['order2'] == self.order_no: 
                self.profit = dictor['profit']
                self.obs_logger.info(f'PROFIT: {self.profit}')
                


    def make_more_candles(self):
        if np.shape(self.minute_1_5box)[0] == 5:
            self.minute_5 = np.array([[
                self.minute_1_5box[-1,0],
                self.minute_1_5box[0,1],
                self.minute_1_5box[-1,2],
                np.max(self.minute_1_5box[:,3]),
                np.min(self.minute_1_5box[:,4]),
                self.minute_1_5box[:,5].sum(),
                self.minute_1_5box[-1,6]]])
            self.minute_1_5box = np.empty(shape=[0, 7])
            self.minute_5_15box = np.vstack([self.minute_5_15box, self.minute_5])
            self.obs_logger.info(f'5MIN: {self.minute_5.tolist()[0]}')

        
        if np.shape(self.minute_5_15box)[0] == 3:
            self.minute_15 = np.array([[
                self.minute_5_15box[-1,0],
                self.minute_5_15box[0,1],
                self.minute_5_15box[-1,2],
                np.max(self.minute_5_15box[:,3]),
                np.min(self.minute_5_15box[:,4]),
                self.minute_5_15box[:,5].sum(),
                self.minute_5_15box[-1,6]]])
            self.minute_5_15box = np.empty(shape=[0, 7])
            self.obs_logger.info(f'15MIN: {self.minute_15.tolist()[0]}')

    def stream(self):
        self.subscribe()
        while self.api.connection_stream == True:
            self.streamread()
            self.make_more_candles()
