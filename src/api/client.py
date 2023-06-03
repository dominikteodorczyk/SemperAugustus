import json
from settings import UserDEMO, UserREAL
from time import sleep
import socket
import ssl
from threading import Thread
import sys
from src.utils.setup_loger import setup_logger

class Client:
    """
    A client that connects to a server in either REAL or DEMO mode.

    Args:
        mode (str): The mode to connect to the server in. Must be either "REAL" or "DEMO".

    Attributes:
        user: A user object representing the user associated with the client.
        socket_connection: A secure socket connection for sending requests to the server.
        socket_stream_connection: A secure socket connection for streaming data from the server.
        login_status (bool): The status of the client's login. None if not logged in.
        stream_session_id (str): The session ID for the client's streaming data session. None if
            not streaming. connection (bool): The status of the client's connection to the server.
            None if not connected.
        connection_stream (bool): The status of the client's streaming data connection to the
            server. None if not connected.

    Raises:
        ValueError: If the mode argument is not "REAL" or "DEMO".
    """

    def __init__(self, mode: str) -> None:

        self.client_logger = setup_logger('client_logger','client.log',print_logs=False)
        self.client_logger.info(f'{mode} SESSION OPENED')

        if mode == "REAL":
            self.user = UserREAL()
        elif mode == "DEMO":
            self.user = UserDEMO()
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

        self.login_status = None
        self.stream_sesion_id = None
        self.connection = None
        self.connection_stream = None

    def connect(self):
        """
        Attempt to connect to the server.
        """
        try:
            self.socket_connection.connect(
                (self.user.host, self.user.main_port)
            )
            self.client_logger.info(f"Connected successfully to {self.user.host}")
            self.connection = True
        except Exception as e:
            self.client_logger.error(f"Not connected to {self.user.host}, {e}")
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
            self.client_logger.info(
                f"Connected successfully to streaming port on {self.user.host}"
            )
            self.connection_stream = True
        except Exception as e:
            self.client_logger.error(
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
            self.client_logger.info(f"Disconnected successfully from {self.user.host}")
            self.connection = False
        except:
            self.client_logger.error(f"Not disconnected from {self.user.host}")
            self.connection = True

    def disconnect_stream(self):
        """
        Disconnects the stream socket connection.
        """
        try:
            self.socket_stream_connection.close()
            self.client_logger.info(
                f"Disconnected successfully stream from {self.user.host}"
            )
            self.connection_stream = False
        except Exception as e:
            self.client_logger.error(f"Not disconnected stream from {self.user.host}")
            self.connection_stream = True

    def send_n_return(self, packet: dict) -> dict:
        """
        Sends a JSON-encoded packet through the connection socket and returns the response.

        Args:
            packet (dict): The packet to be sent.

        Returns:
            dict: The response received from the server.
        """
        command_type = packet["command"]
        message = json.dumps(packet).encode("utf-8")
        received_data = ""
        sent = 0
        while sent < len(message):
            sent += self.socket_connection.send(message[sent:])
        while True:
            char = self.socket_connection.recv(4096).decode()
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
                self.client_logger.warning(f"Error sending {command_type}: {e}")
                continue
        return response

    def stream_send(self, message: dict) -> int:
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
                self.client_logger.warning(f"Reciving error: {e}")
                continue
        return response
        

    def login(self):
        """
        Attempts to log in with the user's credentials and sets the login status, stream
        session ID, and logs relevant messages.
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
            self.client_logger.warning(f"Cant log in, {e}")
        if str(result["status"]) == "True":
            self.login_status = result["status"]
            self.stream_sesion_id = result["streamSessionId"]
            self.client_logger.info(
                f'Logged as {self.user.login} (stream session id: {result["streamSessionId"]})'
            )
        else:
            self.login_status = False
            self.client_logger.error(f"Not logged")

    def logout(self):
        """
        Logs out the user from the server.
        """
        packet = {"command": "logout"}
        result = self.send_n_return(packet)
        if str(result["status"]) == "True":
            self.client_logger.info(f"Logged out of {self.user.login}")
            self.login_status = False
        else:
            self.client_logger.error(f"Not logged out")
            self.login_status = True

    def open_session(self):
        """
        Establishes a session with the server by connecting to the main and streaming ports and
        logging in with the user credentials.

        Raises:
            SystemExit: If the connection cannot be established after six attempts or if the
            login is unsuccessful.
        """
        try:
            for i in range(6):
                try:
                    self.connect()
                    self.connect_stream()
                    break
                except:
                    print("Wait...")
                    sleep(10)
            self.login()
        except:
            self.client_logger.warning(f"Session interrupted, unable to connect.")
            sys.exit(0)

    def close_session(self):
        """
        Closes the session by logging out, disconnecting from the streaming server and the main
        server.
        """
        self.logout()
        self.disconnect_stream()
        self.disconnect()

    def reconnect(self):
        """
        Try to reconnect the client to the server. If the connection is not successful, the
        function will try again for up to 10 times, waiting 5 seconds between attempts. If the
        connection is restored, the client will log in again. If the connection cannot be restored,
        the function will print a warning message and exit the program.
        """
        if self.connection != True:
            for i in range(1, 10):
                try:
                    self.client_logger.info("Trying to reconnect")
                    self.connect()
                    self.connect_stream()
                    self.login()
                    self.client_logger.info("Reconnected")
                    break
                except:
                    self.client_logger.info(
                        "No way to restore the connection. Trying again"
                    )
                    sleep(5)
            if self.connection == None:
                self.client_logger.warning(f"Session interrupted, unable to connect.")
                sys.exit(0)
        else:
            pass


def session_simulator(func) -> tuple:
    """
    A decorator that allows simulated sessions to include a single process as part of testing.

    Args:
        func: A function that needs to be wrapped.

    Returns:
        tuple: A tuple containing the result of the wrapped function, its arguments, and its
            keyword arguments.
    """
    api = Client(mode="DEMO")
    def wrapper(*args, **kwargs):
        api.open_session()
        result = func(api=api, *args, **kwargs)
        api.close_session()
        return result, args, kwargs
    wrapper.attrib = api
    return wrapper


def stream_session_simulator(time):
    """
    Decorator that allows simulated stream sessions to include a single stream process as
    part of testing.

    Parameters:
        time (float): the duration of the stream session in seconds.

    Returns:
        tuple: a tuple that contains the result of the original function,
            along with the arguments and keyword arguments passed to it.
    """

    def decorator(func):
        api = Client(mode="DEMO")
        def wrapper(*args, **kwargs):
            api.open_session()
            object = func(api=api, *args, **kwargs)
            Thread(target=object.stream, args=(), daemon=True).start()
            sleep(time)
            result = object.__dict__
            api.close_session()
            return result, args, kwargs
        wrapper.attrib = api
        return wrapper

    return decorator
