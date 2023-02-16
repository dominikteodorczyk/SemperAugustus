import requests as rq
import os, json
from websocket import create_connection, WebSocketException
from settings import *
import logging
import csv
import pandas as pd



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
        self.connection = None

    def connect(self):
        try:
            self.websocket_conection = create_connection(self.user.websocet)
            logging.info(f'Connected successfully to {self.user.websocet}')
            print(f'Connected successfully to {self.user.websocet}')
            self.connection = True
        except WebSocketException as e:
            logging.error(f'Not connected to {self.user.websocet}, {e}')
            print(f'Not connected to {self.user.websocet}, {e}')
            exit(0)


    def disconnect(self):
        try:
            self.websocket_conection.close()
            logging.info(f'Disconnected successfully from {self.user.websocet}\n')
            print(f'Disconnected successfully from {self.user.websocet}\n')
            self.connection = False
        except:
            logging.error(f'Not disconnected from {self.user.websocet}\n')
            print(f'Not disconnected from {self.user.websocet}\n')
            self.connection = True


    def send(self, packet:dict):
        try:
            self.websocket_conection.send(json.dumps(packet))
            answer = self.websocket_conection.recv()
            return json.loads(answer) 
        except:
            logging.warning('No request has been sent')


    def login(self):
        packet = {
            "command": "login",
            "arguments": {
                "userId": self.user.login,
                "password": self.user.password
                } 
            }
        
        try:
            result = self.send(packet)
        except:
            logging.warning()

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


class RetrievingTradingData():

    def __init__(self) -> None:
        pass


    def command_rtd(func): #wraper do wysyłki komend rtd 
        def wrapped(**kwargs):
            return func(**kwargs)


    def getallsymbols(self):
        packet = {
	        "command": "getAllSymbols"
        }
        return packet

    def getcalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet
    

    def getchartlastrequest(self, parameters:dict):
        packet = {
            "command": "getChartLastRequest",
            "arguments": parameters
            }
        return packet
    

    def getcalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet

    
    def getcalendar(self):
        packet = {
	    "command": "getCalendar"
        }
        return packet
    





def main():
    api = Client('DEMO')
    rtd = RetrievingTradingData()
    api.connect()
    api.login()
    # symbols = api.send(rtd.getcalendar())
    # data_to_csv = symbols['returnData']

    # data = pd.DataFrame()
    # for i in data_to_csv:
    #     data = data.append(i, ignore_index = True)

    # data.to_csv('data.csv', sep='\t')
    api.logout()
    api.disconnect()

if __name__ == "__main__":
    main()