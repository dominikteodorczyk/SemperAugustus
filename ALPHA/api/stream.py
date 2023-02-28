
import json
import numpy as np
from threading import Thread

class WalletStream():

    def __init__(self, api:object) -> None:
        self.api = api
        self.balance = None
        print(self.api.stream_sesion_id)

        self._t = Thread(target=self.stream(), args=())
        self._t.setDaemon(True)
        self._t.start()



    def subscribe(self):
        self.api.send(json.dumps({"command": "getBalance", "streamSessionId": self.api.stream_sesion_id}))


    def streamread(self):
        message = json.loads(self.api.websocket_conection.recv())
        print(message)
        try:
            if message['command'] == 'balance':
                self.balance = np.fromiter(message['data'].values(), dtype=float)
                print(self.balance)
        except:
            pass

    def stream(self):
        self.subscribe()
        while self.api.connection == True:
            self.streamread()
