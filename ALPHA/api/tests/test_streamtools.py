"""
Check the Client of XTB API is valid.
"""

import pytest
from client import *
from streamtools import *


class Test_WalletStream():
      

    # stream duration definition
    @pytest.fixture
    def event_duration(self):
        return 5

    # definition of a stream data duration event using the WalletStream object under test 
    # subscribing to and ad-reading the wallet balance data sent by the API using a decorator 
    # that simulates stream sessions
    @pytest.fixture
    def event(self, event_duration):
        # returns[0] = {api:api, balance:balance}, 
        # returns[1] = args, 
        # returns[2] = kwargs
        return stream_session_simulator(event_duration)(WalletStream)
    




        
    def test_walletstream_is_having_api(self, event):
        results = event()
        assert type(results[0]['api']) is Client # api should be an object of class Client (passed to function from wrapper) 



