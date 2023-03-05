"""
Check the Client of XTB API is valid.
"""

import pytest
from client import *
from settings import UserDEMO
import ssl
import numpy as np
from time import monotonic_ns


class Test_Client():

    def test_Class_demo_atributes(self):
        # collective test of the set of attributes of the created object connecting to the api of the client class 
        APIobject = Client('DEMO')

        # test loading the appropriate classe of user parameters from the settings class
        assert APIobject.user.__class__ is UserDEMO

        # set of parameters which, after defining an instance of the client class, should have the value none
        assert APIobject.login_status is None 
        assert APIobject.stream_sesion_id is None
        assert APIobject.connection is None
        assert APIobject.connection_stream is None

        # create a socket object socketpair for stream and main connection with TLS
        assert type(APIobject.socket_conection) is ssl.SSLSocket
        assert type(APIobject.socket_stream_conection) is ssl.SSLSocket


    def test_Client_method_connect_is_making_connection(self):
        # A test to see if there is a valid connection to the appropriate main port and if there are 
        # changes to the connection confirmation attribute
        APIobject = Client('DEMO')

        APIobject.connect()
        connection = True
        peer_port = UserDEMO().main_port
        
        assert APIobject.socket_conection.getpeername()[1] == peer_port
        assert APIobject.connection is connection


    def test_Client_method_disconnect_is_making_disconnection(self):
        # A test to see if there is a valid stream connection to the appropriate main port and if there are 
        # changes to the stream connection confirmation attribute
        APIobject = Client('DEMO')
        APIobject.connect()

        APIobject.disconnect()
        connection = APIobject.connection
        try:
            APIobject.login()
            failed = False
        except:
            failed = True

        assert connection is False
        assert failed is True # means that the login attempt should fail after disconnection


    def test_Client_method_logs(self):
        # test of the logging method along with checking the change of parameters of the client class object
        APIobject = Client('DEMO')
        APIobject.connect()

        # reading parameters before logging
        status_before_loging = APIobject.login_status
        streamId_before_login = APIobject.stream_sesion_id

        APIobject.login()
        simple_command = {
            "command": "getVersion"
        }

        try:
            recv = APIobject.send_n_return(simple_command)
            recv_status = recv['status'] 
        except:
            recv_status == False

        # statuses should be different before and after
        assert status_before_loging != APIobject.login_status
        assert streamId_before_login != APIobject.stream_sesion_id

        # login status read from server response should be True
        assert APIobject.login_status is True

        # The server's response to the version query is a dictionary with the API version 
        # and status which should be True
        assert recv_status is True


    def test_Client_method_logout_logs_out(self):
        # test of the loggout method along with checking the change of parameters of the client class object
        APIobject = Client('DEMO')
        APIobject.connect()

        # logging and reading the status value returned from the server
        APIobject.login()
        simple_command = {
            "command": "getVersion"
        }

        try:
            recv = APIobject.send_n_return(simple_command)
            recv_status = recv['status'] 
        except:
            recv_status == False
        # reading the value of object parameters after logging in
        status_after_login = APIobject.login_status

        # logout, query dispatch test and reading the value of the login status parameter
        APIobject.logout()
        try:
            recv = APIobject.send_n_return(simple_command)
            recv_status_after_logout = recv['status'] 
        except:
            recv_status_after_logout = False
        status_after_logout = APIobject.login_status

        assert status_after_logout != status_after_login #statuses should be different
        assert recv_status_after_logout != recv_status #statuses should be different


class Test_Decorators():
    # A class of validation tests for decorators to test streaming processes

    def test_Decorator_session_simulator(self):
        # decorator test to simulate the session

        # creating a decorated session_simulation function that sends a command
        # to specify the API version
        @session_simulator
        def simple_function(api, command):
            recv = api.send_n_return(command)
            print(recv)
            recv_status = recv['status']
            return recv_status, api
        
        # command definition 
        simple_command = {
            "command": "getVersion"
        }

        #function_returns is a tulpe of result and used api object
        function_returns, args, kwargs = simple_function(command = simple_command)
        
        assert function_returns[0] is True # return status message sent by the server, should be true
        assert type(function_returns[1]) is Client # api should be an object of class client (passed to function from wrapper
        assert args is () # for 'command = simple_command' the args command is empty
        assert kwargs['command'] == simple_command # used inside the decorator comenda should be consistent with the declared 


    def test_Decorator_stream_session_simulator(self):
        # decorator test to simulate the session

        # creating a decorated session_simulation function that sends a command
        # to specify the API version

        # defining the execution time of the data stream
        time_run = 10
        
        # definition of a class that creates and reads a stream of data on a portfolio
        @stream_session_simulator(time_run)
        class SimpleTestStream():

            def __init__(self, api):
                self.api = api
                self.balance = None

            def subscribe(self):
                return self.api.stream_send({"command": "getBalance", "streamSessionId": self.api.stream_sesion_id})
            
            def streamread(self):
                message = json.loads(self.api.socket_stream_conection.recv())
                try:
                    if message['command'] == 'balance':
                        self.balance = np.fromiter(message['data'].values(), dtype=float)
                except:
                    pass

            def stream(self):
                self.subscribe()
                while self.api.connection_stream == True:
                    self.streamread()

        # measurement of the start of the stream object creation and termination            
        start_runing = monotonic_ns()
        returned = SimpleTestStream()
        time_of_runing_code = monotonic_ns() - start_runing

        # reading the data passed from the stream session simulator decorator
        balance = returned[0]['balance'] # portfolio data 
        api = returned[0]['api'] # api class

        assert np.shape(balance) == (10,) # portfolio data should be of numpy matrix dimension 10x
        assert type(api) == Client # the api used should be of the Client class
        assert time_of_runing_code >= time_run # stream execution time should be longer than declared in the decorator

