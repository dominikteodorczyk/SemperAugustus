import requests as rq
import os, json
from websocket import create_connection

class XTBClientsDEMO():

    def __init__(self) -> None:
        
        self.host = 'xapi.xtb.com'
        self.main_port = 5124
        self.streaming_port = 5125
        self.websocet = 'wss://ws.xtb.com/demo'
        self.websocet_stream = 'wss://ws.xtb.com/demoStream'



class XTBClientsREAL():

    def __init__(self) -> None:
        
        self.host = 'xapi.xtb.com'
        self.main_port = 5112
        self.streaming_port = 5113
        self.websocet = 'wss://ws.xtb.com/real'
        self.websocet_stream = 'wss://ws.xtb.com/realStream'

        print('\033[1;33mWatch out you\'re in the real module\033[0m')


class Client():

    def __init__(self, mode: str) -> None:

        print(f'{mode} SESSION OPENED')

        self.client_main_dir = os.path.dirname(os.path.abspath(__file__))
        self.PASS = open(self.client_main_dir + '\pass.txt').readlines()

        if mode == 'REAL':
            self.XTBClients = XTBClientsREAL()
        
        if mode == 'DEMO':
            self.XTBClients = XTBClientsDEMO()

        self.websocket_conection = None
        self.login_status = None
        self.stream_sesion_id = None


    def connect(self):
        
        try:
            self.websocket_conection = create_connection(self.XTBClients.websocet)
            return print(f'\033[0;32mConnected successfully to {self.XTBClients.websocet}\033[0m\n')

        except:
            return print(f'\033[0;31mNot connected to {self.XTBClients.websocet}\033[0m\n')


    def disconnect(self):
        
        try:
            self.websocket_conection.close()
            return print(f'\n\033[0;32mDisconnected successfully from {self.XTBClients.websocet}\033[0m\n')
        
        except:
            return print(f'\n\033[0;31mNot disconnected from {self.XTBClients.websocet}\033[0m\n')

    def send(self, packet:dict):

        self.websocket_conection.send(json.dumps(packet))
        answer = self.websocket_conection.recv()

        return json.loads(answer) 


    def login(self):

        packet = {
            "command": "login",
            "arguments": {
                "userId": int(self.PASS[1]),
                "password": self.PASS[2]
                } 
            }   

        result = self.send(packet)

        self.login_status = result["status"]
        self.stream_sesion_id = result["streamSessionId"]
        
        if str(result["status"]) == 'True':
            print(f'Login status: \033[0;32m{result["status"]}\033[0m \nStream session id: {result["streamSessionId"]}')

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