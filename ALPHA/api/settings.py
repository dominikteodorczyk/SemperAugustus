from dotenv import load_dotenv
from os import getenv


class UserDEMO():

    def __init__(self) -> None:
        load_dotenv()
        self.login = getenv('XTB_LOGIN_DEMO')
        self.password = getenv('XTB_PASSWORD_DEMO')
        self.host = getenv('XTB_HOST_DEMO')
        self.main_port = getenv('XTB_MAIN_PORT_DEMO')
        self.streaming_port = getenv('XTB_STREAMING_PORT_DEMO')
        self.websocet = getenv('XTB_WEBSOCET_DEMO')
        self.websocet_streaming_port = getenv('XTB_WEBSOCET_STRAMING_PORT_DEMO')


class UserREAL():

    def __init__(self) -> None:
        load_dotenv()
        self.login = getenv('XTB_LOGIN_REAL')
        self.password = getenv('XTB_PASSWORD_REAL')
        self.host = getenv('XTB_HOST_REAL')
        self.main_port = getenv('XTB_MAIN_PORT_REAL')
        self.streaming_port = getenv('XTB_STREAMING_PORT_REAL')
        self.websocet = getenv('XTB_WEBSOCET_REAL')
        self.websocet_streaming_port = getenv('XTB_WEBSOCET_STRAMING_PORT_REAL')