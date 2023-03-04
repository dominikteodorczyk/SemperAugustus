"""
Check the Client of XTB API is valid.
"""

import pytest
from client import Client
from settings import UserDEMO
import ssl


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
