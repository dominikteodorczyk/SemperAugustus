
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
        self.open_stream_data_M1 = None
        self.open_stream_data_M5 = None
        self.candle_1M = None
        self.candle_5M = None
        self.candle_15M = None
        self.candle_1H = None
        self.price = None

    def keepalive(self):
        return self.api.stream_send({"command": "getKeepAlive", "streamSessionId": self.api.stream_sesion_id})

    def subscribe(self):
        return self.api.stream_send({"command": "getBalance", "streamSessionId": self.api.stream_sesion_id})      

    def stream():
        pass
