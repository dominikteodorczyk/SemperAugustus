"""
Module containing clients objects for api and wrappers for testing clients.
"""

import json
import socket
import ssl
import sys
from threading import Thread
from typing import Union, Callable, Any
from time import sleep
from settings import XTBUserDEMO, XTBUserREAL
from utils.technical import setup_logger


class XTBClient:
    """
    A client that connects to a server in either REAL or DEMO mode.

    Args:
        mode (str): The mode to connect to the server in. Must be either
        "REAL" or "DEMO".

    Attributes:
        user: A user object representing the user associated with the client.
        socket_connection: A secure socket connection for sending requests
            to the server.
        socket_stream_connection: A secure socket connection for streaming
            data from the server.
        login_status (bool): The status of the client's login. None if not
            logged in.
        stream_session_id (str): The session ID for the client's streaming
            data session. None if not streaming.
        connection (bool): The status of the client's connection to the
            server. None if not connected.
        connection_stream (bool): The status of the client's streaming data
            connection to the server. None if not connected.

    Raises:
        ValueError: If the mode argument is not "REAL" or "DEMO".
    """

    def __init__(self, mode: str) -> None:
        self.logging = setup_logger(
            "client_logger", "client.log", print_logs=False
        )
        self.logging.info(f"{mode} SESSION OPENED")

        if mode == "REAL":
            self.user: Union[XTBUserREAL, XTBUserDEMO] = XTBUserREAL()
        elif mode == "DEMO":
            self.user = XTBUserDEMO()
        else:
            raise ValueError(
                "Invalid mode argument. Must be either 'REAL' or 'DEMO'."
            )

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_connection = ssl.wrap_socket(
            sock, ssl_version=ssl.PROTOCOL_TLS
        )

        sock_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_stream_connection = ssl.wrap_socket(
            sock_stream, ssl_version=ssl.PROTOCOL_TLS
        )

        self.login_status: bool = False
        self.stream_sesion_id: str = str()
        self.connection: bool = False
        self.connection_stream: bool = False

    def connect(self):
        """
        Attempt to connect to the server.
        """
        try:
            self.socket_connection.connect(
                (self.user.host, self.user.main_port)
            )
            self.logging.info(f"Connected successfully to {self.user.host}")
            self.connection = True
        except Exception as e:
            self.logging.error(f"Not connected to {self.user.host}, {e}")
            self.connection = False
            sys.exit(0)

    def connect_stream(self):
        """
        Attempt to connect to the server's streaming port.
        """
        try:
            self.socket_stream_connection.connect(
                (self.user.host, self.user.streaming_port)
            )
            self.logging.info(
                f"Connected successfully to streaming port on {self.user.host}"
            )
            self.connection_stream = True
        except Exception as e:
            self.logging.error(
                f"Not connected to streaming port on {self.user.host}, {e}"
            )
            self.connection_stream = False
            sys.exit(0)

    def disconnect(self):
        """
        Attempt to disconnect from the server.
        """
        try:
            self.socket_connection.close()
            self.logging.info(
                f"Disconnected successfully from {self.user.host}"
            )
            self.connection = False
        except Exception as e:
            self.logging.error(
                f"Not disconnected from {self.user.host}, " f"details: {e}"
            )
            self.connection = True

    def disconnect_stream(self):
        """
        Disconnects the stream socket connection.
        """
        try:
            self.socket_stream_connection.close()
            self.logging.info(
                f"Disconnected successfully stream from {self.user.host}"
            )
            self.connection_stream = False
        except Exception as e:
            self.logging.error(
                f"Not disconnected stream from {self.user.host} details: {e}"
            )
            self.connection_stream = True

    def send_n_return(
        self, packet: dict[Any, Any]
    ) -> dict[str, Union[int, float, str, bool]]:
        """
        Sends a JSON-encoded packet through the connection socket and returns
        the response.

        Args:
            packet (dict): The packet to be sent.

        Returns:
            dict: The response received from the server.
        """
        command_type: str = packet["command"]
        message: bytes = json.dumps(packet).encode("utf-8")
        received_data: str = ""
        sent: int = 0
        response: dict[str, Union[int, float, str, bool]]
        while sent < len(message):
            sent += self.socket_connection.send(message[sent:])
        while True:
            char: str = self.socket_connection.recv(4096).decode()
            received_data += char
            try:
                (response, size) = json.JSONDecoder().raw_decode(received_data)
                if size == len(received_data):
                    received_data = ""
                    break
                elif size < len(received_data):
                    received_data = received_data[size:].strip()
                    break
            except Exception as e:
                self.logging.warning(f"Error sending {command_type}: {e}")
                continue
        return response

    def stream_send(self, message: dict[str, Any]) -> int:
        """
        Sends a JSON-encoded message through the stream connection socket.

        Args:
            message (dict): A dictionary representing the message to be sent.

        Returns:
            int: message from server.
        """
        return self.socket_stream_connection.send(
            json.dumps(message).encode("utf-8")
        )

    def stream_read(self):
        """
        Method that reads data streamed by api.

        Returns:
            int: message from server.
        """
        received_data = ""
        while True:
            char = self.socket_stream_connection.recv(4096).decode()
            received_data += char
            try:
                (response, size) = json.JSONDecoder().raw_decode(received_data)
                if size == len(received_data):
                    received_data = ""
                    break
                elif size < len(received_data):
                    received_data = received_data[size:].strip()
                    break
            except Exception as e:
                self.logging.warning(f"Reciving error: {e}")
                continue
        return response

    def login(self):
        """
        Attempts to log in with the user's credentials and sets
        the login status, stream session ID, and logs relevant messages.
        """
        packet = {
            "command": "login",
            "arguments": {
                "userId": self.user.login,
                "password": self.user.password,
            },
        }
        try:
            result = self.send_n_return(packet)
        except Exception as e:
            self.logging.warning(f"Cant log in, {e}")
        if result["status"] is True and isinstance(
            result["streamSessionId"], str
        ):
            self.login_status = result["status"]
            self.stream_sesion_id = result["streamSessionId"]
            self.logging.info(
                f"Logged as {self.user.login}"
                f"(stream session id: {result['streamSessionId']})"
            )
        else:
            self.login_status = False
            self.logging.error("Not logged")

    def logout(self):
        """
        Logs out the user from the server.
        """
        packet = {"command": "logout"}
        result = self.send_n_return(packet)
        if str(result["status"]) == "True":
            self.logging.info(f"Logged out of {self.user.login}")
            self.login_status = False
        else:
            self.logging.error("Not logged out")
            self.login_status = True

    def open_session(self):
        """
        Establishes a session with the server by connecting to the main
        and streaming ports and logging in with the user credentials.

        Raises:
            SystemExit: If the connection cannot be established after
                six attempts or if the login is unsuccessful.
        """
        try:
            for i in range(6):
                try:
                    self.connect()
                    self.connect_stream()
                    break
                except ConnectionError as e:
                    self.logging.info(f"Wait... {e}")
                    sleep(10)
            self.login()
        except ConnectionError as e:
            self.logging.warning(
                f"Session interrupted, unable to connect. Details: {e}"
            )
            sys.exit(0)

    def close_session(self):
        """
        Closes the session by logging out, disconnecting from the streaming
        server and the main server.
        """
        self.logout()
        self.disconnect_stream()
        self.disconnect()

    def reconnect(self):
        """
        Try to reconnect the client to the server. If the connection is not
        successful, the function will try again for up to 10 times, waiting
        5 seconds between attempts. If the  connection is restored, the client
        will log in again. If the connection cannot be restored, the function
        will print a warning message and exit the program.
        """
        if self.connection is not True:
            for i in range(1, 10):
                try:
                    self.logging.info("Trying to reconnect")
                    self.connect()
                    self.connect_stream()
                    self.login()
                    self.logging.info("Reconnected")
                    break
                except ConnectionError:
                    self.logging.info(
                        "No way to restore the connection. Trying again"
                    )
                    sleep(5)
            if self.connection is False:
                self.logging.warning("Session interrupted, unable to connect.")
                sys.exit(0)
        else:
            pass


def session_simulator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that allows simulated sessions to include a single process as
    part of testing.

    Args:
        func: A function that needs to be wrapped.

    Returns:
        Callable: A wrapped function.
    """
    client = XTBClient(mode="DEMO")

    def wrapper(*args, **kwargs) -> Any:
        client.open_session()
        result: Any = func(client=client, *args, **kwargs)
        client.close_session()
        return result, args, kwargs

    return wrapper


def stream_session_simulator(time: int) -> Any:
    """
    Decorator that allows simulated stream sessions to include a single
    stream process as
    part of testing.

    Parameters:
        time (int): the duration of the stream session in seconds.

    Returns:
        tuple: a tuple that contains the result of the original function,
            along with the arguments and keyword arguments passed to it.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        client = XTBClient(mode="DEMO")

        def wrapper(*args, **kwargs):
            client.open_session()
            object = func(client=client, *args, **kwargs)
            Thread(target=object.stream, args=(), daemon=True).start()
            sleep(time)
            result = object.__dict__
            client.close_session()
            return result, args, kwargs

        return wrapper

    return decorator
