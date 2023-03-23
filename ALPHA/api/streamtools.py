import json
import numpy as np

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
        message = json.loads(self.api.socket_stream_conection.recv())
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


class AssetBOX():

    def __init__(self, api=None, symbol=None) -> None:
        self.api = api
        self.symbol = symbol
        self.minute_1 = None
        self.minute_5 = None
        self.minute_15 = None

        self.minute_1_5box = np.empty(shape=[0, 7])
        self.minute_5_15box = np.empty(shape=[0, 7])


    def keepalive(self):
        return self.api.stream_send({"command": "getKeepAlive", "streamSessionId": self.api.stream_sesion_id})

    def subscribe(self):
        return self.api.stream_send({"command": "getCandles", "streamSessionId": self.api.stream_sesion_id, "symbol": "EURUSD"})    

    def streamread(self):
        message = json.loads(self.api.socket_stream_conection.recv())
        if message['command'] == 'candle':
            dictor=message["data"]
            dictor.pop('ctmString')
            dictor.pop('symbol')
            self.minute_1 = np.fromiter(dictor.values(), dtype=float).reshape(1,7)
            self.minute_1_5box = np.vstack([self.minute_1_5box, self.minute_1])
            print('1MIN: ',self.minute_1,)


    def make_more_candles(self):
        if np.shape(self.minute_1_5box)[0] is 5:
            self.minute_5 = np.array([[
                self.minute_1_5box[4,0],
                self.minute_1_5box[0,1],
                self.minute_1_5box[4,2],
                np.max(self.minute_1_5box[:,3]),
                np.min(self.minute_1_5box[:,4]),
                self.minute_1_5box[:,5].sum(),
                self.minute_1_5box[-1,6]]])
            self.minute_1_5box = np.empty(shape=[0, 7])
            self.minute_5_15box = np.vstack([self.minute_5_15box, self.minute_5])
            print('5MIN:',self.minute_5)
        
        if np.shape(self.minute_5_15box)[0] is 3:
            self.minute_15 = np.array([[
                self.minute_5[2,0],
                self.minute_5[0,1],
                self.minute_5[2,2],
                np.max(self.minute_5[:,3]),
                np.min(self.minute_5[:,4]),
                self.minute_5[:,5].sum(),
                self.minute_5[-1,6]]])
            self.minute_5_15box = np.empty(shape=[0, 7])
            print('15MIN:',self.minute_15)

    def stream(self):
        self.subscribe()
        while self.api.connection_stream == True:
            self.streamread()
            self.make_more_candles()



