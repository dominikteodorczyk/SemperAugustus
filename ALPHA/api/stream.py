
import json
import numpy as np
from threading import Thread

class WalletStream():

    def __init__(self, api:object) -> None:
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
                print(self.balance)
        except:
            pass

    def stream(self):
        self.subscribe()
        while self.api.connection_stream == True:
            self.streamread()
            self.keepalive()