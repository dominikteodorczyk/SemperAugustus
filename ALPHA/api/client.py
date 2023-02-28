import os, json
from websocket import create_connection, WebSocketException
from settings import *
import logging
from commands import RetrievingTradingData
from time import sleep
from stream import WalletStream
from threading import Thread
import time



class Client():

    def __init__(self, mode: str) -> None:

        logging.basicConfig(filename='ALPHA\log\client.log',level=logging.INFO, format='%(asctime)s.%(msecs)04d - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.info(f'{mode} SESSION OPENED')
        logging

        self.client_main_dir = os.path.dirname(os.path.abspath(__file__))
        if mode == 'REAL':
            self.user = UserREAL()
        if mode == 'DEMO':
            self.user = UserDEMO()

        self.websocket_conection = None
        self.login_status = None
        self.stream_sesion_id = None
        self.connection = None

        self.websocket_stream_conection = None
        self.connection_stream = None



    def connect(self):
        try:
            self.websocket_conection = create_connection(self.user.websocet)
            logging.info(f'Connected successfully to {self.user.websocet}')
            print(f'Connected successfully to {self.user.websocet}')
            self.connection = True
        except WebSocketException as e:
            logging.error(f'Not connected to {self.user.websocet}, {e}')
            print(f'Not connected to {self.user.websocet}, {e}')
            self.connection = False
            exit(0)
            
    def connect_stream(self):
        try:
            self.websocket_stream_conection = create_connection(self.user.websocet_streaming_port)
            logging.info(f'Connected successfully to {self.user.websocet_streaming_port}')
            print(f'Connected successfully to {self.user.websocet_streaming_port}')
            self.connection_stream = True
        except WebSocketException as e:
            logging.error(f'Not connected to {self.user.websocet_streaming_port}, {e}')
            print(f'Not connected to {self.user.websocet_streaming_port}, {e}')
            self.connection_stream = False
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


    def send_n_return(self, packet:dict):
        try:
            self.websocket_conection.send(json.dumps(packet))
            answer = self.websocket_conection.recv()
            return json.loads(answer) 
        except:
            logging.warning('No request has been sent')

    def stream_send(self, message:dict):

        self.websocket_stream_conection.send(json.dumps(message))



    def login(self):
        packet = {
            "command": "login",
            "arguments": {
                "userId": self.user.login,
                "password": self.user.password
                } 
            }
        
        try:
            result = self.send_n_return(packet)
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
        result = self.send_n_return(packet)
        if str(result["status"]) == 'True':
            print(f'Logout status: {result["status"]}')
            logging.info(f'Logged out of {self.user.login}')
        else:
            print(f'Not logged out')
            logging.error(f'Not logged out')

    
    def opensession(self):

        for i in range(6):
            try:
                self.connect()
                self.connect_stream()
                break
            except:
                print('Wait...')
                sleep(10)
        if self.connection == False or None:
            print(f'Session interrupted, unable to connect.')
            logging.warning(f'Session interrupted, unable to connect.')
            exit(0) 
        


        self.login()

    def closesession(self):
        self.logout()
        self.disconnect()


    def reconnect(self):
        if self.connection == False or None:
            print('Wait..')
            for i in range(1,10):
                try:
                    logging.info('Trying to reconnect')
                    self.connect()
                    self.login()
                    logging.info('Reconnected')
                    break
                except:
                    logging.info('No way to restore the connection. Trying again')
                    sleep(1)
            if self.connection == None:
                print(f'Session interrupted, unable to connect.')
                logging.warning(f'Session interrupted, unable to connect.')
                exit(0) 
        else:
            pass





def main():
    api = Client('DEMO')
    api.opensession()

    wallet = WalletStream(api=api)
    wallet.stream()

    # time.sleep(30)

    api.closesession()




if __name__ == "__main__":
    main()
