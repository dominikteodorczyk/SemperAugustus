"""
Function tests in the commands module.
"""

from unittest.mock import MagicMock, patch
import pytest
from api.commands import get_trades, get_margin, buy_transaction


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
        assert isinstance(trade_return, dict)

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

    def test_get_trades_make_loop_until_get_data(self, get_trades_msg):
        """
        Test if the function performed several iterations until it got the
        correct data
        """
        client = MagicMock()
        client.send_n_return.side_effect = [None, None, None, get_trades_msg]
        get_trades(client=client, order_no=1234567)
        assert client.send_n_return.call_count == 4


class Test_get_margin:
    """
    Test of the get margin function returning the margin calculated by the
    broker for the expected position.
    """

    @pytest.fixture
    def get_margin_msg(self):
        return {"status": True, "returnData": {"margin": 4399.350}}

    @pytest.fixture
    def get_margin_return(self):
        return 4399.350

    def test_is_margin_return_float_if_get_data(self, get_margin_msg):
        """
        Whether the function returns a float.
        """
        client = MagicMock()
        client.send_n_return.return_value = get_margin_msg
        margin_return = get_margin(client=client, symbol="EURPLN", volume=1.0)
        assert isinstance(margin_return, float)

    def test_is_margin_return_return_expected_margin_value(
        self, get_margin_msg, get_margin_return
    ):
        """
        Whether the function returns a expected margin.
        """
        client = MagicMock()
        client.send_n_return.return_value = get_margin_msg
        margin_return = get_margin(client=client, symbol="EURPLN", volume=1.0)
        assert margin_return == get_margin_return


class Test_buy_transaction:
    """
    Module to test functions that execute a buy order.
    """
    @pytest.fixture
    def buy_response(self):
        return {"status": True, "returnData": {"order": 1234567}}

    @pytest.fixture
    def get_margin_return(self):
        return 4399.350

    @pytest.fixture
    def get_trades_return(self):
        return {
            "symbol": "EURUSD",
            "order": 1234567,
            "position": 1234567,
            "cmd": 1,
            "volume": 0.10,
            "open_price": 1.4,
            "open_time": 1272380927000,
        }

    @pytest.fixture
    def buy_transaction_return(self):
        return {
            "margin": 4399.35,
            "order_no": 1234567,
            "transactions_data": {
                "symbol": "EURUSD",
                "order": 1234567,
                "position": 1234567,
                "cmd": 1,
                "volume": 0.10,
                "open_price": 1.4,
                "open_time": 1272380927000,
            },
        }

    def test_is_buy_transaction_return_dict(
        self, buy_response, get_margin_return, get_trades_return
    ):
        """
        Test to check if a function returns a dictionary.
        """
        client = MagicMock()
        client.send_n_return.return_value = buy_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ) as mock_get_margin_function, patch(
            "api.commands.get_trades", return_value=get_trades_return
        ) as mock_get_trades_function:
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert isinstance(position_data, dict)

    def test_is_buy_transaction_return_dict_with_margin_key(
        self, buy_response, get_margin_return, get_trades_return
    ):
        """
        Test if there is a margin key in the returned dictionary
        """
        client = MagicMock()
        client.send_n_return.return_value = buy_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ) as mock_get_margin_function, patch(
            "api.commands.get_trades", return_value=get_trades_return
        ) as mock_get_trades_function:
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert 'margin' in position_data

    def test_is_buy_transaction_return_dict_with_order_no_key(
        self, buy_response, get_margin_return, get_trades_return
    ):
        """
        Test if there is a order_no key in the returned dictionary
        """
        client = MagicMock()
        client.send_n_return.return_value = buy_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ) as mock_get_margin_function, patch(
            "api.commands.get_trades", return_value=get_trades_return
        ) as mock_get_trades_function:
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert 'order_no' in position_data

    def test_is_buy_transaction_return_dict_with_transactions_data_no_key(
        self, buy_response, get_margin_return, get_trades_return
    ):
        """
        Test if there is a transactions_data key in the returned dictionary
        """
        client = MagicMock()
        client.send_n_return.return_value = buy_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ) as mock_get_margin_function, patch(
            "api.commands.get_trades", return_value=get_trades_return
        ) as mock_get_trades_function:
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert 'transactions_data' in position_data

    def test_is_buy_transaction_return_expected_dict(
        self, buy_response, get_margin_return, get_trades_return, buy_transaction_return
    ):
        """
        Test to validate the returned data.
        """
        client = MagicMock()
        client.send_n_return.return_value = buy_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ) as mock_get_margin_function, patch(
            "api.commands.get_trades", return_value=get_trades_return
        ) as mock_get_trades_function:
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert position_data == buy_transaction_return

