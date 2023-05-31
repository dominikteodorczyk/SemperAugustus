from api.client import Client
from api.commands import buy_transaction, sell_transaction
from threading import Thread
from models.close_signals import *
from models.trends import MovingAVG
from time import sleep
from utils.setup_loger import setup_logger
from utils.wallet import Wallet
from utils.technical_utils import SessionTechnicalController
import logging


class TradingSession(object):

    def __init__(self, symbols:list = None) -> None:
        self.symbols = symbols
        # init object with risk data and portfolio management
        self.wallet = Wallet() 
        # init object containing data on technical aspects of the session 
        # such as (spread, volume levels, volatility)
        self.session_control = SessionTechnicalController(symbols=symbols)
        # init trading pool object of all symbols
        self.trading_pool = TradingPool(symbols = symbols)
        

    def session_init(self):
        # Initialization of threads for the risk manager, session controller and trading pool
        wallet_thread = Thread(
            target=self.wallet.run, 
            args=())
        
        session_control_thread = Thread(
            target=self.session_control.run, 
            args=())
        
        trading_pool_thread = Thread(
            target=self.trading_pool.run_pool, 
            args=(self.wallet, self.session_control))

        wallet_thread.start()
        session_control_thread.start()
        trading_pool_thread.start()

        wallet_thread.join()
        session_control_thread.join()
        trading_pool_thread.join()

#TODO: moduł testowany na końcu
class TradingPool(object):

    def __init__(self, symbols) -> None:
        self.symbols = symbols

    def run_pool(self, risk_data, session_data):
        self.risk_data = risk_data
        self.session_data = session_data
        
        slots = []
        for symbol in self.symbols:
            thread = Thread(
                target=TradingSlot(symbol).run_slot, 
                args=(self.risk_data, self.session_data))
            thread.start()
            slots.append(thread)
        
        for slot in slots: slot.join()


class TradingSlot(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.symbol_data = DataStream(symbol=self.symbol)
        # self.open_model = MovingAVG()
        # self.close_model = DefaultCloseSignal()

    def run_slot(self, risk_data, session_data):
        # data stream thread with a separate api client
        data_thread = Thread(
            target=self.symbol_data.run, 
            args=())
        # trading thread on a given symbol using stream data for the symbol, 
        # as well as risk and technical session fitness data
        position_thread = Thread(
            target=Trader(symbol=self.symbol).run, 
            args=(self.symbol_data, risk_data,session_data,))

        data_thread.start()
        position_thread.start()

        data_thread.join()
        position_thread.join()


class Trader(object):
    def __init__(self,symbol) -> None:
        self.symbol = symbol
        self.buy_model = MovingAVG(symbol=symbol,period=1)

    def open_position(self):
        while True:
            position = Position(
                cmd=self.buy_model.signal,
                symbol=self.symbol,
                volume=0.01,
                close_signal=DefaultCloseSignal(),
            )

            position.run()


    def run(self,symbol_data, risk_data,session_data):
        buy_model_thread = Thread(
            target=self.buy_model.run,
            args=(symbol_data,))
        
        position_thread = Thread(
            target=self.open_position,
            args=())
        buy_model_thread.start()

        while True:
            if self.buy_model.signal == None:
                sleep(1)
                pass
            else:
                break

        position_thread.start()
        buy_model_thread.join()
        position_thread.join()


class Position:
    def __init__(
        self, cmd, symbol: str, volume: float, close_signal: object = None
    ):
        self.api = Client('DEMO')
        self.cmd = cmd
        self.symbol = symbol
        self.volume = volume
        self.close_signal = close_signal
        self.position_logger = setup_logger(
            f"{self.symbol}-{self.cmd}-", "src\log\position_logger.log"
        )

    def run(self):
        self.api.open_session()
        if self.cmd == 0:
            self.order = buy_transaction(
                api=self.api, symbol=self.symbol, volume=self.volume
            )
            self.close_signal.init(api=self.api, position_data=self.order, sl_start= 1.5)
            self.close_signal.run()
        if self.cmd == 1:
            self.order = sell_transaction(
                api=self.api, symbol=self.symbol, volume=self.volume
            )
            self.close_signal.init(api=self.api, position_data=self.order, sl_start= 1.5)
            self.close_signal.run()

        profit = self.close_signal.closedata["profit"]
        self.position_logger.info(
            f'{self.order["order_no"]} CLOSED WITH PROFIT: {profit}'
        )
        self.api.close_session()



    # TODO: całość powyższa powinna odbywać się w close signal i to
    # on powinien wykonywać operacje zamknięcia pozycji wraz z jej monitoringiem,
    # w ten sposob uniknie się komplikacji kody i wielokrotnego przekazywania zmienny

    # TODO: clasa powinna zwracac profit zakończonej transackji jej numery, długośc
    # raz wykorzystane modele do zawarcia transacki oraz zakończenia

