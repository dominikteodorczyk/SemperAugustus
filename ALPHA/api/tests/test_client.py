import pytest
from ALPHA.api.client import *
from ALPHA.api.settings import *
import ssl


class Test_Client():

    def test_Class_demo_atributes(self):

        from client import Client
        from settings import UserDEMO
        import ssl

        object = Client('DEMO')

        # test loading the appropriate classe of user parameters from the settings class
        assert object.user.__class__ is UserDEMO

        # set of parameters which, after defining an instance of the client class, should have the value none
        assert object.login_status is None 
        assert object.stream_sesion_id is None
        assert object.connection is None
        assert object.connection_stream is None

        # create a socket object socketpair for stream and main connection with TLS
        assert type(object.socket_conection) is ssl.SSLSocket
        assert type(object.socket_stream_conection) is ssl.SSLSocket

    