from api.client import Client
from api.streamtools import WalletStream, AssetObservator
from api.commands import buy_transaction, sell_transaction


class TradingSlot():

    def __init__(self, api, symbol, volume):
        self.symbol = symbol
        self.api = api
        self.volume = volume
    
    def observe_symbol(self):
        pass

    def buy_signal(self):
        pass


    def open_trade(self):
        arguments = {
                    "tradeTransInfo": {
                        "cmd": 0,
                        "customComment": "SEAU_algo",
                        "expiration": 0,
                        "order": 0,
                        "price": 1.4,
                        "sl": 0,
                        "tp": 0,
                        "symbol": self.symbol,
                        "type": 0,
                        "volume": self.volume
                    }
                }
        
        self.api.stream_send()
        

class TradingSession():
    
    def __init__(self):
        self.api = Client('DEMO')

    def session():
        pass

def buy_now():
    api = Client('DEMO')
    api.open_session()
    #response = buy_transaction(api=api,symbol='BINANCECOIN',volume=0.3)
    data = sell_transaction(api=api,symbol='EURUSD',volume=0.3)
    print(data)
    api.close_session()
