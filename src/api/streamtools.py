"""
Data streaming tools
"""

from threading import Thread
from copy import copy
from time import sleep
import numpy as np
from typing import Any
from api.client import XTBClient
from utils.technical import setup_logger


class WalletStream:
    """
    Represents a wallet data stream.

    Args:
        client(XTBClient): The API client object associated with
            the wallet stream.

    Attributes:
        client: The API client object associated with the wallet stream.
        balance: The balance of the wallet.
    """

    def __init__(self) -> None:
        self.client = XTBClient("DEMO")
        self.balance: np.ndarray[Any, np.dtype[Any]] = np.array([])

    def subscribe(self) -> None:
        """
        Subscribes to portfolio data for obtaining stream data from api.
        """
        self.client.stream_send(
            {
                "command": "getBalance",
                "streamSessionId": self.client.stream_sesion_id,
            }
        )

    def read_stream(self) -> None:
        """
        Reads data from the stream and writes it to the balance
        class attribute.
        """
        message = self.client.stream_read()
        try:
            if message["command"] == "balance":
                self.balance = np.fromiter(
                    message["data"].values(), dtype=float
                )
        except Exception:
            # skip if there is no portfolio balance data in the stream
            pass

    def stream(self) -> None:
        """
        Begins subscriptions and continuous stream data reading.
        """
        self.client.open_session()
        self.subscribe()
        while self.client.connection_stream is True:
            self.read_stream()


class PositionObservator:
    """
    Class of objects observing data about the candle profic and the current
    price of the concluded position

    Args:
        client (XTBClient): The API client object associated with the
            PositionObservator.
        symbol (str): The symbol associated with the PObservator.
        order_no (int): The order number associated with the PObservator.

    Attributes:
        logging: The logger object for recording observations.
        client (XTBClient): The API client object associated with the
            PositionObservator.
        symbol (str): The symbol associated with the PositionObservator.
        order_no (int): The order number associated with the
            PositionObservator.
        current_price: An array to store the current price observations.
        profit: The profit associated with the PositionObservator.
        minute_1: An array to store candles at 1-minute intervals.
        minute_5: An array to store candles at 5-minute intervals.
        minute_15: An array to store candles at 15-minute intervals.
        minute_1_5box: An array to store candles at 1-minute intervals
            using a 5-box method.
        minute_5_15box: An array to store candles at 5-minute intervals
            using a 15-box method.
    """

    def __init__(self, client: XTBClient, symbol: str, order_no: int) -> None:
        self.logging = setup_logger(
            f"{symbol}-{order_no}", "obs_logger.log", print_logs=False
        )
        self.client = client
        self.symbol = symbol
        self.order_no = order_no
        self.curent_price = np.empty(shape=[0, 11])
        self.profit: float = 0.0
        self.minute_1 = np.empty(shape=[0, 7])
        self.minute_5 = np.empty(shape=[0, 7])
        self.minute_15 = np.empty(shape=[0, 7])
        self.minute_1_5box = np.empty(shape=[0, 7])
        self.minute_5_15box = np.empty(shape=[0, 7])

    def subscribe(self):
        """
        Subscribes to candles, tick price and profits data for obtaining
        stream data from api.
        """
        self.client.stream_send(
            {
                "command": "getCandles",
                "streamSessionId": self.client.stream_sesion_id,
                "symbol": self.symbol,
            }
        )
        self.client.stream_send(
            {
                "command": "getTickPrices",
                "streamSessionId": self.client.stream_sesion_id,
                "symbol": self.symbol,
            }
        )
        self.client.stream_send(
            {
                "command": "getProfits",
                "streamSessionId": self.client.stream_sesion_id,
            }
        )

    def read_stream(self):
        """
        Reads data from the stream and writes it to the class attributes.
        """
        message = self.client.stream_read()
        if message["command"] == "tickPrices":
            # 'ask','bid','high','low','askVolume','bidVolume',
            # 'timestamp','level','quoteId','spreadTable','spreadRaw'
            dictor = copy(message["data"])
            if dictor["symbol"] == self.symbol:
                dictor.pop("symbol")
                self.curent_price = np.fromiter(
                    dictor.values(), dtype=float
                ).reshape(1, 11)
        if message["command"] == "profit":
            dictor = copy(message["data"])
            if dictor["order2"] == self.order_no:
                self.profit = dictor["profit"]
        if message["command"] == "candle":
            dictor = copy(message["data"])
            # 'ctm', 'open', 'close', 'high', 'low', 'vol', 'quoteId'
            if dictor["symbol"] == self.symbol:
                dictor.pop("ctmString")
                dictor.pop("symbol")
                self.minute_1 = np.fromiter(
                    dictor.values(), dtype=float
                ).reshape(1, 7)
                self.minute_1_5box = np.vstack(
                    [self.minute_1_5box, self.minute_1]
                )

    def make_more_candles(self):
        """
        Aggregates candles to a higher interval
        """
        if np.shape(self.minute_1_5box)[0] == 5:
            self.minute_5 = np.array(
                [
                    [
                        self.minute_1_5box[-1, 0],
                        self.minute_1_5box[0, 1],
                        self.minute_1_5box[-1, 2],
                        np.max(self.minute_1_5box[:, 3]),
                        np.min(self.minute_1_5box[:, 4]),
                        self.minute_1_5box[:, 5].sum(),
                        self.minute_1_5box[-1, 6],
                    ]
                ]
            )
            self.minute_1_5box = np.empty(shape=[0, 7])
            self.minute_5_15box = np.vstack(
                [self.minute_5_15box, self.minute_5]
            )

        if np.shape(self.minute_5_15box)[0] == 3:
            self.minute_15 = np.array(
                [
                    [
                        self.minute_5_15box[-1, 0],
                        self.minute_5_15box[0, 1],
                        self.minute_5_15box[-1, 2],
                        np.max(self.minute_5_15box[:, 3]),
                        np.min(self.minute_5_15box[:, 4]),
                        self.minute_5_15box[:, 5].sum(),
                        self.minute_5_15box[-1, 6],
                    ]
                ]
            )
            self.minute_5_15box = np.empty(shape=[0, 7])

    def stream(self):
        """
        Starts stream reading and candle aggregation
        """
        self.read_stream()
        self.make_more_candles()


class DataStream:
    """
    Class of data stream objects on the valor used in the trading slot.

    Args:
        symbol: The symbol associated with the DataStream.

    Attributes:
        client: The API client object associated with the DataStream.
        symbol: The symbol associated with the DataStream.
        server_time: The server time of the DataStream.
        tick_msg: The tick message of the DataStream.
        candle_msg: The candle message of the DataStream.
        symbols_price: An array to store symbol prices.
        symbols_last_1M: An array to store last 1-minute symbols data.
        stream_logger: The logger object for the data stream.
    """

    def __init__(self, symbol: str):
        self.client = XTBClient("DEMO")
        self.symbol = symbol
        self.server_time = None
        self.tick_msg: dict[str, Any] = {}
        self.candle_msg: dict[str, Any] = {}
        self.symbols_price = np.empty(shape=[0, 11])
        self.symbols_last_1M = np.empty(shape=[0, 7])
        self.stream_logger = setup_logger(
            name=f"[DATASTREAM] {symbol}",
            log_file_name="data_stream.log",
            print_logs=True,
        )

    def subscribe(self):
        """
        Subscribes to tick price and candles data for obtaining stream
        data from api.
        """
        self.client.stream_send(
            {
                "command": "getTickPrices",
                "streamSessionId": self.client.stream_sesion_id,
                "symbol": self.symbol,
            }
        )
        self.client.stream_send(
            {
                "command": "getCandles",
                "streamSessionId": self.client.stream_sesion_id,
                "symbol": self.symbol,
            }
        )

    def is_connected(self):
        """
        Method for env monitoring
        """
        if self.client.connection_stream is True:
            return True
        else:
            return False

    def read_stream_messages(self):
        """
        Reads data from the stream and writes it to the class attributes
        (candle or tick).
        """
        while self.is_connected() is True:
            message = self.client.stream_read()
            if message["command"] == "tickPrices":
                self.tick_msg = message
            if message["command"] == "candle":
                self.candle_msg = message

    def read_prices(self):
        """
        Aggregates price msg.
        """
        while self.is_connected() is True:
            try:
                dictor = self.tick_msg["data"]
                # 'ask','bid','high','low','askVolume','bidVolume',
                # 'timestamp','level','quoteId','spreadTable','spreadRaw'
                dictor.pop("symbol")
                self.symbols_price = np.fromiter(
                    dictor.values(), dtype=float
                ).reshape(1, 11)
            except Exception:
                sleep(0.5)

    def read_last_1M(self):
        """
        Aggregates candles msg.
        """
        while self.is_connected() is True:
            try:
                dictor = self.candle_msg["data"]
                # 'ctm', 'open', 'close', 'high', 'low', 'vol', 'quoteId'
                for key in ["symbol", "quoteId", "ctmString"]:
                    dictor.pop(key)
                self.symbols_last_1M = np.fromiter(
                    dictor.values(), dtype=float
                ).reshape(1, 6)
            except Exception:
                sleep(1)

    def run(self):
        """
        Data subscraptions, and threads for reading messages from
        the stream and aggregating them into prices and candles to
        minimize the probability of lost messages.
        """
        self.client.open_session()
        self.subscribe()
        thread_read = Thread(target=self.read_stream_messages, args=())
        thread_prices = Thread(target=self.read_prices, args=())
        thread_candles = Thread(target=self.read_last_1M, args=())

        thread_read.start()
        while True:
            if not self.candle_msg and not self.tick_msg:
                sleep(1)
            else:
                break
        print("started")  # FIXME: make some loger
        thread_prices.start()
        thread_candles.start()

        thread_read.join()
        thread_prices.join()
        thread_candles.join()

        self.client.close_session()
