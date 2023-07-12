"""
Function tests in the commands module.
"""

import pytest
from unittest.mock import MagicMock
from api.commands import get_trades, get_margin


class Test_get_trades:
    """
    Test class of the function "get_trades" that allows to get full data
    about the concluded transaction located on the broker's server
    """

    @pytest.fixture
    def get_trades_msg(self):
        return {
            "status": True,
            "returnData": [
                {
                    "close_price": 1.3256,
                    "close_time": 0,
                    "close_timeString": "",
                    "closed": False,
                    "cmd": 0,
                    "comment": "Web Trader",
                    "commission": 0.0,
                    "customComment": "Some text",
                    "digits": 4,
                    "expiration": "",
                    "expirationString": "",
                    "margin_rate": 0.0,
                    "offset": 0,
                    "open_price": 1.4,
                    "open_time": 1272380927000,
                    "open_timeString": "Fri Jan 11 10:03:36 CET 2013",
                    "order": 7497776,
                    "order2": 1234567,
                    "position": 1234567,
                    "profit": -2196.44,
                    "sl": 0.0,
                    "storage": -4.46,
                    "symbol": "EURUSD",
                    "timestamp": 1272540251000,
                    "tp": 0.0,
                    "volume": 0.10,
                }
            ],
        }

    @pytest.fixture
    def get_trades_return(self):
        return {
            "symbol": "EURUSD",
            "order": 1234567,
            "position": 1234567,
            "cmd": 0,
            "volume": 0.10,
            "open_price": 1.4,
            "open_time": 1272380927000,
        }

    def test_its_get_trades_return_dict(self, get_trades_msg):
        """
        Test to check the type returned by the function is to be a dictionary).
        """
        client = MagicMock()
        client.send_n_return.return_value = get_trades_msg
        trade_return = get_trades(client=client, order_no=1234567)
        assert type(trade_return) is dict

    def test_ist_get_trades_return_expected_message(
        self, get_trades_msg, get_trades_return
    ):
        """
        Does the function return the expected value of the expected message.
        """
        client = MagicMock()
        client.send_n_return.return_value = get_trades_msg
        trade_return = get_trades(client=client, order_no=1234567)
        assert trade_return == get_trades_return

    def test_get_trades_send_requests_as_long_get_trades_data(
        self, get_trades_msg, get_trades_return
    ):
        """
        Test if function returns correct data after several failures
        """
        client = MagicMock()
        client.send_n_return.side_effect = [None, None, None, get_trades_msg]
        trade_return = get_trades(client=client, order_no=1234567)
        assert trade_return == get_trades_return

    def test_get_trades_make_loop_until_get_data(
        self, get_trades_msg, get_trades_return
    ):
        """
        Test if the function performed several iterations until it got the
        correct data
        """
        client = MagicMock()
        client.send_n_return.side_effect = [None, None, None, get_trades_msg]
        get_trades(client=client, order_no=1234567)
        assert client.send_n_return.call_count == 4

class Test_get_margin():
    """
    Test of the get margin function returning the margin calculated by the
    broker for the expected position.
    """
    @pytest.fixture
    def get_margin_msg(self):
        return {
            "status": True,
            "returnData": {
                "margin": 4399.350
            }
        }

    @pytest.fixture
    def get_margin_return(self):
        return 4399.350

    def test_is_margin_return_float_if_get_data(self,get_margin_msg):
        """
        Whether the function returns a float.
        """
        client = MagicMock()
        client.send_n_return.return_value = get_margin_msg
        margin_return = get_margin(client=client, symbol='EURPLN', volume = 1.0)
        assert type(margin_return) == float

    def test_is_margin_return_return_expected_margin_value(self,get_margin_msg,get_margin_return):
        """
        Whether the function returns a expected margin.
        """
        client = MagicMock()
        client.send_n_return.return_value = get_margin_msg
        margin_return = get_margin(client=client, symbol='EURPLN', volume = 1.0)
        assert margin_return == get_margin_return