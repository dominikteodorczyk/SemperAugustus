import os, json
from settings import *
import logging
from commands import RetrievingTradingData
from time import sleep
from stream import WalletStream
from threading import Thread
import socket
import ssl



class Client():

    def __init__(self, mode: str) -> None:

        logging.basicConfig(filename='ALPHA\log\client.log',level=logging.INFO, format='%(asctime)s.%(msecs)04d - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logging.info(f'{mode} SESSION OPENED')

        if mode == 'REAL':
            self.user = UserREAL()
        if mode == 'DEMO':
            self.user = UserDEMO()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_conection = ssl.wrap_socket(sock, ssl_version = ssl.PROTOCOL_TLS)

        sock_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_stream_conection = ssl.wrap_socket(sock_stream, ssl_version = ssl.PROTOCOL_TLS)

        self.login_status = None
        self.stream_sesion_id = None
        self.connection = None
        self.connection_stream = None

    def connect(self):
        try:
            self.socket_conection.connect((self.user.host, self.user.main_port))
            logging.info(f'Connected successfully to {self.user.host}')
            print(f'Connected successfully to {self.user.host}')
            self.connection = True
        except Exception as e:
            logging.error(f'Not connected to {self.user.host}, {e}')
            print(f'Not connected to {self.user.host}, {e}')
            self.connection = False
            exit(0)
            
    def connect_stream(self):
        try:
            self.socket_stream_conection.connect((self.user.host, self.user.streaming_port))
            logging.info(f'Connected successfully stream to {self.user.host}')
            print(f'Connected successfully stream to {self.user.host}')
            self.connection_stream = True
        except Exception as e:
            logging.error(f'Not connected stream to {self.user.host}, {e}')
            print(f'Not connected stream to {self.user.host}, {e}')
            self.connection_stream = False
            exit(0)

    def disconnect(self):
        try:
            self.socket_conection.close()
            logging.info(f'Disconnected successfully from {self.user.host}\n')
            print(f'Disconnected successfully from {self.user.host}\n')
            self.connection = False
        except:
            logging.error(f'Not disconnected from {self.user.host}\n')
            print(f'Not disconnected from {self.user.host}\n')
            self.connection = True

    def disconnect_stream(self):
        try:
            self.socket_stream_conection.close()
            logging.info(f'Disconnected successfully stream from {self.user.host}')
            print(f'Disconnected successfully stream from {self.user.host}')
            self.connection_stream = False
        except Exception as e:
            logging.error(f'Not disconnected stream from {self.user.host}')
            print(f'Not disconnected stream from {self.user.host}')
            self.connection_stream = True


    def send_n_return(self, packet:dict):
        try:
            self.socket_conection.send(json.dumps(packet).encode('utf-8'))
            answer = self.socket_conection.recv()
            return json.loads(answer) 
        except Exception as e:
            logging.warning(f'No request has been sent, {e}')

    def stream_send(self, message:dict):
        return self.socket_stream_conection.send(json.dumps(message).encode('utf-8'))

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
            self.login_status = False
        else:
            print(f'Not logged out')
            logging.error(f'Not logged out')
            self.login_status = True
    
    def opensession(self):

        try:
            for i in range(6):
                try:
                    self.connect()
                    self.connect_stream()
                    break
                except:
                    print('Wait...')
                    sleep(10)
            self.login()
        except:
            print(f'Session interrupted, unable to connect.')
            logging.warning(f'Session interrupted, unable to connect.')
            exit(0) 

    def closesession(self):
        self.logout()
        self.disconnect_stream()
        self.disconnect()

    def reconnect(self):
        if self.connection != True:
            print('Wait..')
            for i in range(1,10):
                try:
                    print(f'Trying to reconnect')
                    logging.info('Trying to reconnect')
                    self.connect()
                    self.connect_stream()
                    self.login()
                    print(f'Reconnected')
                    logging.info('Reconnected')
                    break
                except:
                    print(f'No way to restore the connection. Trying again')
                    logging.info('No way to restore the connection. Trying again')
                    sleep(5)
            if self.connection == None:
                print(f'Session interrupted, unable to connect.')
                logging.warning(f'Session interrupted, unable to connect.')
                exit(0) 
        else:
            pass



def main():
    api = Client('DEMO')
    api.opensession()
    api.closesession()


if __name__ == "__main__":
    main()
