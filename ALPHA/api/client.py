import requests as rq
import os, json
from websocket import create_connection
from settings import *


class Client():

    def __init__(self, mode: str) -> None:
        print(f'{mode} SESSION OPENED')
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
            return print(f'\033[0;32mConnected successfully to {self.user.websocet}\033[0m\n')
        except:
            return print(f'\033[0;31mNot connected to {self.user.websocet}\033[0m\n')

    def disconnect(self):
        try:
            self.websocket_conection.close()
            return print(f'\n\033[0;32mDisconnected successfully from {self.user.websocet}\033[0m\n')
        except:
            return print(f'\n\033[0;31mNot disconnected from {self.user.websocet}\033[0m\n')

    def send(self, packet:dict):
        self.websocket_conection.send(json.dumps(packet))
        answer = self.websocket_conection.recv()
        return json.loads(answer) 

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
            print(f'Login status: \033[0;32m{result["status"]}\033[0m \nStream session id: {result["streamSessionId"]}')
            self.login_status = result["status"]
            self.stream_sesion_id = result["streamSessionId"]
        else:
            print(f'Login status: \033[0;31m{result["status"]}\033[0m')


    def logout(self):
        packet = {
            "command": "logout"
            }   
        result = self.send(packet)
        if str(result["status"]) == 'True':
            print(f'Logout status: \033[0;32m{result["status"]}\033[0m')
        else:
            print(f'Logout status: \033[0;31m{result["status"]}\033[0m')


def main():
    api = Client('DEMO')
    api.connect()
    api.login()
    api.logout()
    api.disconnect()

if __name__ == "__main__":
    main()