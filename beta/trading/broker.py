from api.client import Client
from api.streamtools import WalletStream, PositionObservator
from api.commands import buy_transaction, sell_transaction, close_position
from threading import Thread
from models.close_signals import *
from models.trends import MovingAVG
from time import sleep
from utils.setup_loger import setup_logger





class TradingSlot:
    def __init__(self, api, symbol):
        self.symbol = symbol
        self.api = api


class Position:
    def __init__(
        self, api, cmd, symbol: str, volume: float, close_signal: object = None
    ):
        self.api = api
        self.symbol = symbol
        self.volume = volume
        self.cmd = cmd
        self.close_signal = close_signal
        self.position_logger = setup_logger(
            f"{self.symbol}-{self.cmd}-", "beta\log\position_logger.log"
        )

    def run(self):
        if self.cmd == 0:
            self.order = buy_transaction(
                api=self.api, symbol=self.symbol, volume=self.volume
            )
            self.position_logger.info(f'{self.order["order_no"]} OPENED')
            self.close_signal.init(api=self.api, position_data=self.order)
            self.close_signal.run()
        if self.cmd == 1:
            self.order = sell_transaction(
                api=self.api, symbol=self.symbol, volume=self.volume
            )
            self.position_logger.info(f'{self.order["order_no"]} OPENED')
            self.close_signal.init(api=self.api, position_data=self.order)
            self.close_signal.run()

        profit = self.close_signal.closedata["profit"]
        self.position_logger.info(
            f'{self.order["order_no"]} CLOSED WITH PROFIT: {profit}'
        )
        return profit

    # TODO: całość powyższa powinna odbywać się w close signal i to
    # on powinien wykonywać operacje zamknięcia pozycji wraz z jej monitoringiem,
    # w ten sposob uniknie się komplikacji kody i wielokrotnego przekazywania zmienny

    # TODO: clasa powinna zwracac profit zakończonej transackji jej numery, długośc
    # raz wykorzystane modele do zawarcia transacki oraz zakończenia


class PrinterSybolsA:
    def __init__(self) -> None:
        self.zmienna = 0

    def print_data(self, data):
        while True:
            # print(data)
            self.zmienna += 1
            # print(self.zmienna)
            sleep(1)


class TradingSession:
    def __init__(self, symbols: list = None):
        # self.api = Client('DEMO')
        # ['BITCOIN','BINANCECOIN','AAVE','APECOIN','FANTOM','DOGECOIN']

        self.printerA = PrinterSybolsA()
        self.printerB = PrinterSybolsA()

    def sessionA(self):
        api = Client("DEMO")
        api.open_session()
        symbol_dataA = DataStream(api=api, symbols=["BITCOIN", "BINANCECOIN"])
        thread_prices = Thread(target=symbol_dataA.runAA, args=())
        thread_print = Thread(
            target=self.printerA.print_data, args=(symbol_dataA.symbols_price,)
        )
        thread_prices.start()
        # thread_print.start()
        thread_prices.join()
        # thread_print.join()
        api.connection_stream = False
        api.close_session()

    def sessionB(self):
        api = Client("DEMO")
        api.open_session()
        symbol_dataB = DataStream(api=api, symbols=["FANTOM", "DOGECOIN"])
        thread_prices = Thread(target=symbol_dataB.runAA, args=())
        thread_print = Thread(
            target=self.printerB.print_data, args=(symbol_dataB.symbols_price,)
        )

        thread_prices.start()
        # thread_print.start()
        thread_prices.join()
        # thread_print.join()
        api.connection_stream = False
        api.close_session()

    def run(self):
        symbol_thread_1 = Thread(target=self.sessionA, args=())
        symbol_thread_2 = Thread(target=self.sessionB, args=())

        symbol_thread_1.start()
        symbol_thread_2.start()

        sleep(20)

        symbol_thread_1.join()
        symbol_thread_2.join()


def position():
    api = Client("DEMO")
    api.open_session()
    model = MovingAVG(api=api, symbol="BITCOIN", period=1)
    model.run()
    sleep(5)
    while api.connection_stream == True:
        cmd = model.signal
        print(f"Pozycja: {cmd}")
        position = Position(
            api=api,
            cmd=cmd,
            symbol="BITCOIN",
            volume=0.01,
            close_signal=DefaultCloseSignal(),
        )

        position_result = position.run()
        if position_result < 0 and cmd == 1:
            cmd = 0
        elif position_result < 0 and cmd == 0:
            cmd = 1
        else:
            pass

        sleep(2)

    api.close_session()
