"""
The module allows you to run a trading session with the use of an entry model
and an exit model.
"""

from time import sleep
from threading import Thread
from api.client import Client
from api.commands import buy_transaction, sell_transaction
from api.streamtools import DataStream
from models.close_signals import DefaultCloseSignal
from models.trends import MovingAVG
from utils.technical import setup_logger
from utils.wallet import Wallet
from utils.controlling import AssetTechnicalController



class TradingSession():
    """
    Trading session object supporting multi-threaded monitoring of portfolio risk,
    technical aspects of the session and trading slot pools for defined symbols.

    Args:
        symbols (list): A list of symbols associated with the trading session.

    Attributes:
        symbols (list): A list of symbols associated with the trading session.
        wallet: The wallet object for managing the session's portfolio. Init object
            with risk data and portfolio management (functionality under development).
        session_control: The session technical controller object for managing
            technical aspects of the session such as spread, volume levels,
            volatility (functionality under development).
        trading_pool: The trading pool object for all symbols in the session.
    """

    def __init__(self, symbols: list) -> None:
        self.symbols = symbols
        self.wallet = Wallet()
        self.session_control = AssetTechnicalController(symbol='symbols') #FIXME: to change in the future
        self.trading_pool = TradingPool(symbols=symbols)

    def session_init(self):
        """
        Initialization of threads for the risk manager, session controller and trading pool
        """

        wallet_thread = Thread(target=self.wallet.run, args=())
        session_control_thread = Thread(target=self.session_control.run, args=())
        trading_pool_thread = Thread(
            target=self.trading_pool.run_pool, args=(self.wallet, self.session_control)
        )

        wallet_thread.start()
        session_control_thread.start()
        trading_pool_thread.start()

        wallet_thread.join()
        session_control_thread.join()
        trading_pool_thread.join()


class TradingPool():
    """
    Facility that manages the slots of individual trading symbols

    Args:
        symbols (list): A list of symbols associated with the trading pool.

    Attributes:
        symbols (list): A list of symbols associated with the trading pool.
            risk_data: Risk management data - position size or value of
                starting stoplos (functionality in plans)
            session_data: Data on the proper functioning of stock market
                and sessions - Market Maker's work efficiency
                (functionality in plans)
    """
    def __init__(self, symbols:list) -> None:
        self.symbols = symbols
        self.risk_data = None
        self.session_data = None

    def run_pool(self, risk_data, session_data):
        """
        Starts thread pools for all defined symbols.

        Args:
            risk_data: Risk management data - position size or value of
                starting stoplos (functionality in plans)
            session_data: Data on the proper functioning of stock market
                and sessions - Market Maker's work efficiency
                (functionality in plans)
        """

        self.risk_data = risk_data
        self.session_data = session_data

        # Starts thread pools
        slots = []
        for symbol in self.symbols:
            thread = Thread(
                target=TradingSlot(symbol).run_slot,
                args=(self.risk_data, self.session_data),
            )
            thread.start()
            slots.append(thread)

        for slot in slots:
            slot.join()


class TradingSlot():
    """
    Trading slot object for the selected symbol. The running slot
    supports a thread of streaming data about the given symbol
    (candles and current price) and a thread of the Trader making
    decisions about entering and exiting positions.

    Args:
        symbol (str): The symbol associated with the trading slot.

    Attributes:
        symbol (str): The symbol associated with the trading slot.
        symbol_data: The data stream object for the symbol.
    """

    def __init__(self, symbol:str) -> None:
        self.symbol = symbol
        # Data stream of the symbol
        self.symbol_data = DataStream(symbol=self.symbol)

    def run_slot(self, risk_data, session_data):
        """
        Starts the trading slot of a given symbol. Starts two
        threads - the data stream and the Trader.

        Args:
            risk_data: Risk management data - position size or value of
                starting stoplos (functionality in plans)
            session_data: Data on the proper functioning of stock market
                and sessions - Market Maker's work efficiency
                (functionality in plans)
        """

        # data stream thread with a separate api client
        data_thread = Thread(target=self.symbol_data.run, args=())
        # trading thread on a given symbol using stream data for the symbol,
        # as well as risk and technical session fitness data
        position_thread = Thread(
            target=Trader(symbol=self.symbol).run,
            args=(
                self.symbol_data,
                risk_data,
                session_data,
            ),
        )

        data_thread.start()
        position_thread.start()

        data_thread.join()
        position_thread.join()


class Trader():
    """
    Represents a trader for a specific symbol.

    Args:
        symbol (str): The symbol to trade.

    Attributes:
        symbol (str): The symbol being traded.
        buy_model (MovingAVG): The moving average model used for
            buying decisions.
    """
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.buy_model = MovingAVG(symbol=symbol, period=1)

    def open_position(self):
        """
        Initiates an Position object with the specified parameters.
        The function is executed continuously in a while loop containing
        the next transaction after the previous one is completed according
        to the instructions contained in the buy_model class attribute.

        TODO:change the pattern in the future, and use the risk manager
        to calculate the size of the position
        """
        while True:
            position = Position(
                cmd=self.buy_model.signal,
                symbol=self.symbol,
                volume=0.01,
                close_signal=DefaultCloseSignal(),
            )
            position.run()

    def run(self, symbol_data, risk_data, session_data):
        """
        Runs the threads for buy model and position.

        Args:
            symbol_data: Data coming from a stream of data on the symbol
                rather than the item
            risk_data: Risk management data - position size or value of
                starting stoplos (functionality in plans)
            session_data: Data on the proper functioning of stock market
                and sessions - Market Maker's work efficiency
                (functionality in plans)
        """

        buy_model_thread = Thread(target=self.buy_model.run, args=(symbol_data,))
        position_thread = Thread(target=self.open_position, args=())
        buy_model_thread.start()

        # block holding the conclusion of the position until the data is
        # calculated by the purchasing model
        while True:
            if self.buy_model.signal is None:
                sleep(1)
            else:
                break

        position_thread.start()
        buy_model_thread.join()
        position_thread.join()


class Position():
    """
    Represents a trading position.

    Args:
        cmd (int): The command for the position.
        symbol (str): The symbol associated with the position.
        volume (float, optional): The volume for the
            position (default: 0.01).
        close_signal (object, optional): The close signal for
            the position (default: DefaultCloseSignal()).

    Attributes:
        client: The client object for trading.
        order: atribut for order data
        cmd (int): The command for the position.
        symbol (str): The symbol associated with the position.
        volume (float): The volume for the position.
        close_signal: The close signal for the position.
        logging: The logger for position-related logs.
    """

    def __init__(
        self,
        cmd: int,
        symbol: str,
        volume: float = 0.01,
        close_signal: object = DefaultCloseSignal(),
    ):
        self.client = Client("DEMO")
        self.order = None
        self.cmd = cmd
        self.symbol = symbol
        self.volume = volume
        self.close_signal = close_signal
        self.logging = setup_logger(
            f"{self.symbol}-{self.cmd}-", "position_logger.log"
        )

    def run(self):
        """
        Executes the position and logs the result.
        """
        self.client.open_session()

        if self.cmd == 0:
            self.order = buy_transaction(
                client=self.client, symbol=self.symbol, volume=self.volume
            )
        if self.cmd == 1:
            self.order = sell_transaction(
                client=self.client, symbol=self.symbol, volume=self.volume
            )
        #Combination of sl_start parameter (percentage value of position rate)
        self.close_signal.set_params(
                client=self.client, position_data=self.order, sl_start=1.5
            )
        self.close_signal.run()
        profit = self.close_signal.closedata["profit"]
        self.logging.info(
            f'{self.order["order_no"]} CLOSED WITH PROFIT: {profit}'
        )
        self.client.close_session()
