"""
Module containing objects that create data classes that configure the operation
of the apllication
"""

from os import getenv, path, makedirs
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


class XTBUserDEMO:
    """A class representing a user for XTB demo account.

    Attributes:
        login (str): The login credential for the XTB demo trading account.
        password (str): The password credential for the XTB demo trading account.
        host (str): The host or server address for connecting to the XTB API
            in demo trading mode.
        main_port (int): The main port number for establishing a connection with
            the XTB API in demo trading mode.
        streaming_port (int): The streaming port number for real-time data from
            the XTB API in demo trading mode.
        websocket (str): The WebSocket URL for connecting to the XTB API in demo
            trading mode.
        websocket_streaming_port (str): The WebSocket streaming port number for
            real-time data from the XTB API in demo trading mode.
    """

    def __init__(self) -> None:
        """
        Initialize a new UserDEMO instance. This constructor loads the required
        environment variables and initializes the instance variables.
        """

        load_dotenv()
        self.login = getenv("XTB_LOGIN_DEMO")
        self.password = getenv("XTB_PASSWORD_DEMO")
        self.host = getenv("XTB_HOST_DEMO")
        self.main_port = int(getenv("XTB_MAIN_PORT_DEMO", "O"))
        self.streaming_port = int(getenv("XTB_STREAMING_PORT_DEMO", "O"))
        self.websocket = getenv("XTB_WEBSOCKET_DEMO")
        self.websocket_streaming_port = getenv(
            "XTB_WEBSOCKET_STREAMING_PORT_DEMO"
        )


class XTBUserREAL:
    """
    UserREAL class represents a user for XTB real trading. It provides the necessary
    credentials and connection information to interact with the XTB API in the
    real trading environment.

    Attributes:
        login (str): The login credential for the XTB real trading account.
        password (str): The password credential for the XTB real trading account.
        host (str): The host or server address for connecting to the XTB API in
            real trading mode.
        main_port (int): The main port number for establishing a connection with
            the XTB API in real trading mode.
        streaming_port (int): The streaming port number for real-time data from
            the XTB API in real trading mode.
        websocket (str): The WebSocket URL for connecting to the XTB API in real
            trading mode.
        websocket_streaming_port (str): The WebSocket streaming port number for
            real-time data from the XTB API in real trading mode.
    """

    def __init__(self) -> None:
        load_dotenv()
        self.login = getenv("XTB_LOGIN_REAL")
        self.password = getenv("XTB_PASSWORD_REAL")
        self.host = getenv("XTB_HOST_REAL")
        self.main_port = int(getenv("XTB_MAIN_PORT_REAL", "O"))
        self.streaming_port = int(getenv("XTB_STREAMING_PORT_REAL", "O"))
        self.websocket = getenv("XTB_WEBSKOCET_REAL")
        self.websocket_streaming_port = getenv(
            "XTB_WEBSOCKET_STRAMING_PORT_REAL"
        )


class LoggerPaths:
    """
    LoggerPaths class represents the paths for logging files.

    Attributes:
        log_path (str): The path for the log files.
    """

    def __init__(self) -> None:
        load_dotenv(verbose=True)
        self.log_path = path.join(
            path.dirname(__file__), getenv("DEF_LOG_PATH", "O")
        )
        if not path.exists(self.log_path):
            makedirs(self.log_path)


class DataBases:
    BASE = declarative_base()
    DATA_PATH = path.join(path.dirname(__file__), "data")

    def __init__(self) -> None:
        if not path.exists(DataBases.DATA_PATH):
            makedirs(DataBases.DATA_PATH)
        self.transactions = path.join(DataBases.DATA_PATH, "transactions.db")
        self.create_databases()
        print(self.transactions)

    def create_databases(self):
        for attribute_name, attribute_value in vars(self).items():
            if not path.exists(attribute_value):
                self.create_new_database(path=attribute_value)

    def create_new_database(self, path):
        engine = create_engine(f"sqlite:///{path}")
        DataBases.BASE.metadata.create_all(engine)
