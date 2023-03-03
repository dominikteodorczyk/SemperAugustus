"""
Check the numpy config is valid.
"""

import pytest
from client import *
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

    def test_Client_method_connect_is_making_stream_connection(self):
        # A test to see if there is a valid stream connection to the appropriate main port and if there are 
        # changes to the stream connection confirmation attribute
        APIobject = Client('DEMO')

        APIobject.connect_stream()
        connection = True
        peer_port = UserDEMO().streaming_port
        
        assert APIobject.socket_stream_conection.getpeername()[1] == peer_port
        assert APIobject.connection_stream is connection