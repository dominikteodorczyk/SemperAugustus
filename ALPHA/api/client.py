import requests as rq
import os, json
from websocket import create_connection
from settings import *
import logging



class Client():

    def __init__(self, mode: str) -> None:

        logging.basicConfig(filename='ALPHA\logging\client.log',level=logging.INFO, format='%(asctime)s.%(msecs)04d - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.info(f'{mode} SESSION OPENED')

        self.client_main_dir = os.path.dirname(os.path.abspath(__file__))
        if mode == 'REAL':
            self.user = UserREAL()
        if mode == 'DEMO':
            self.user = UserDEMO()

        self.websocket_conection = None
        self.login_status = None
        self.stream_sesion_id = None

    def connect(self):
        try:
            self.websocket_conection = create_connection(self.user.websocet)
            logging.info(f'Connected successfully to {self.user.websocet}')
            print(f'Connected successfully to {self.user.websocet}')
        except:
            logging.error(f'Not connected to {self.user.websocet}')
            print(f'Not connected to {self.user.websocet}')

    def disconnect(self):
        try:
            self.websocket_conection.close()
            logging.info(f'Disconnected successfully from {self.user.websocet}\n')
            print(f'Disconnected successfully from {self.user.websocet}\n')
        except:
            logging.error(f'Not disconnected from {self.user.websocet}\n')
            print(f'Not disconnected from {self.user.websocet}\n')

    def send(self, packet:dict):
        try:
            self.websocket_conection.send(json.dumps(packet))
            answer = self.websocket_conection.recv()
            return json.loads(answer) 
        except:
            pass

    def login(self):
        packet = {
            "command": "login",
            "arguments": {
                "userId": self.user.login,
                "password": self.user.password
                } 
            }
        
        result = self.send(packet)

        if str(result["status"]) == 'True':
            print(f'Login status: {result["status"]}, stream session id: {result["streamSessionId"]}')
            self.login_status = result["status"]
            self.stream_sesion_id = result["streamSessionId"]
            logging.info(f'Logged as {self.user.login} (stream session id: {result["streamSessionId"]})')
        else:
            print(f'Login status: {result["status"]}')
            logging.error(f'Not logged')

    def logout(self):
        packet = {
            "command": "logout"
            }   
        result = self.send(packet)
        if str(result["status"]) == 'True':
            print(f'Logout status: {result["status"]}')
            logging.info(f'Logged out of {self.user.login}')
        else:
            print(f'Not logged out')
            logging.error(f'Not logged out')


def main():
    api = Client('DEMO')
    api.connect()
    api.login()
    api.logout()
    api.disconnect()

if __name__ == "__main__":
    main()