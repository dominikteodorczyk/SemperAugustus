"""
Check the Client of XTB API is valid.
"""

import pytest
from client import *
from streamtools import *


class Test_WalletStream():

    @pytest.fixture
    def event():

        @stream_session_simulator
        def wallet_stream():
            return WalletStream()
        
        return wallet_stream()
        
        
    def test_walletstream_is_having_api(self, event):

        results = event()




