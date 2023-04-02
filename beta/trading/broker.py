from api.client import Client
from api.streamtools import WalletStream, PositionObservator
from api.commands import buy_transaction, sell_transaction
from threading import Thread
from models.default_close_signals import *


class TradingSlot():

    def __init__(self, api, symbol):
        self.symbol = symbol
        self.api = api
        
        
class Position():

    def __init__(
            self, api, cmd, symbol: str, 
            volume:float, close_signal:object = DefaultCloseSignal()):
        self.api = api
        self.symbol = symbol
        self.volume = volume
        self.cmd = cmd
        self.close_signal = close_signal

        if self.cmd == 0:
            self.order = buy_transaction(
                api=self.api,symbol=self.symbol,volume=self.volume
            )
            self.close_signal.run()
        if self.cmd == 1:
            self.order = sell_transaction(
                api=self.api,symbol=self.symbol,volume=self.volume
            )
            self.close_signal.run()

        self.current_price = None
        self.current_wallet_banace = None
        self.current_return = None
        self.minute_1 = None
        self.minutes_5 = None
        self.minutes_15 = None
        
        self.walet_stream = WalletStream(api=api)
        self.price_data = PositionObservator(api=api,symbol=self.symbol)
        self.status_to_close = False

    def subscribe_data(self):
        self.walet_stream.subscribe()
        self.price_data.subscribe()

    def read_data(self):
        self.current_wallet_banace = self.walet_stream.balance
        self.current_price = self.price_data.curent_price
        self.current_return = self.price_data.profit
        self.minute_1 = self.price_data.minute_1
        self.minutes_5 = self.price_data.minute_5
        self.minutes_15 = self.price_data.minute_15

    def sefault_close_position(self):
        pass

    def run_position(self):
        self.subscribe_data()
        while self.status_to_close is False:
            self.walet_stream.streamread()
            self.price_data.streamread()
            self.read_data()


    #TODO: całość powyższa powinna odbywać się w close signal i to 
    # on powinien wykonywać operacje zamknięcia pozycji wraz z jej monitoringiem,
    # w ten sposob uniknie się komplikacji kody i wielokrotnego przekazywania zmienny

    #TODO: clasa powinna zwracac profit zakończonej transackji jej numery, długośc 
    # raz wykorzystane modele do zawarcia transacki oraz zakończenia
        
    
        





class TradingSession():
    
    def __init__(self):
        self.api = Client('DEMO')

    def session():
        pass

def position():
    api = Client('DEMO')
    api.open_session()
    position_data = sell_transaction(api=api,symbol='BITCOIN',volume=0.01)
    print(position_data)
    PositionObservator(api=api, symbol='BITCOIN', order_no=position_data['order_no']).stream()
    api.close_session()
