"""
Function tests in the commands module.
"""

from unittest.mock import MagicMock, patch
import pytest
import numpy as np
from api.commands import (
    get_trades,
    get_margin,
    buy_transaction,
    sell_transaction,
    close_position,
    get_historical_candles
)


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
        ), patch("api.commands.get_trades", return_value=get_trades_return):
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
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert "margin" in position_data

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
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert "order_no" in position_data

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
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert "transactions_data" in position_data

    def test_is_buy_transaction_return_expected_dict(
        self,
        buy_response,
        get_margin_return,
        get_trades_return,
        buy_transaction_return,
    ):
        """
        Test to validate the returned data.
        """
        client = MagicMock()
        client.send_n_return.return_value = buy_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = buy_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert position_data == buy_transaction_return


class Test_sell_transaction:
    """
    Module to test functions that execute a sell order.
    """

    @pytest.fixture
    def sell_response(self):
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
    def sell_transaction_return(self):
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

    def test_is_sell_transaction_return_dict(
        self, sell_response, get_margin_return, get_trades_return
    ):
        """
        Test to check if a function returns a dictionary.
        """
        client = MagicMock()
        client.send_n_return.return_value = sell_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = sell_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert isinstance(position_data, dict)

    def test_is_sell_transaction_return_dict_with_margin_key(
        self, sell_response, get_margin_return, get_trades_return
    ):
        """
        Test if there is a margin key in the returned dictionary
        """
        client = MagicMock()
        client.send_n_return.return_value = sell_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = sell_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert "margin" in position_data

    def test_is_sell_transaction_return_dict_with_order_no_key(
        self, sell_response, get_margin_return, get_trades_return
    ):
        """
        Test if there is a order_no key in the returned dictionary
        """
        client = MagicMock()
        client.send_n_return.return_value = sell_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = sell_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert "order_no" in position_data

    def test_is_buy_transaction_return_dict_with_transactions_data_no_key(
        self, sell_response, get_margin_return, get_trades_return
    ):
        """
        Test if there is a transactions_data key in the returned dictionary
        """
        client = MagicMock()
        client.send_n_return.return_value = sell_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = sell_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert "transactions_data" in position_data

    def test_is_buy_transaction_return_expected_dict(
        self,
        sell_response,
        get_margin_return,
        get_trades_return,
        sell_transaction_return,
    ):
        """
        Test to validate the returned data.
        """
        client = MagicMock()
        client.send_n_return.return_value = sell_response
        with patch(
            "api.commands.get_margin", return_value=get_margin_return
        ), patch("api.commands.get_trades", return_value=get_trades_return):
            position_data = sell_transaction(
                client=client, symbol="EURUSD", volume=0.10
            )
            assert position_data == sell_transaction_return


class Test_close_position:
    """
    Tests of the close position function for closing an open position
    and returning a dictionary with the final data of the transaction
    (result)
    """

    @pytest.fixture
    def close_returned_message(self):
        return {"status": True, "returnData": {"order": 1234567}}

    @pytest.fixture
    def first_trading_history_response(self):
        return {
            "close_price": 1.7256,
            "close_time": 1272380967000,
            "close_timeString": 0,
            "closed": 0,
            "cmd": 0,
            "comment": "Web Trader",
            "commission": 0.0,
            "customComment": "Some text",
            "digits": 4,
            "expiration": 0,
            "expirationString": 0,
            "margin_rate": 0.0,
            "offset": 0,
            "open_price": 1.4,
            "open_time": 1272380927000,
            "open_timeString": "Fri Jan 11 10:03:36 CET 2013",
            "order": 7497776,
            "order2": 1234567,
            "position": 1234567,
            "profit": 2196.44,
            "sl": 0.0,
            "storage": -4.46,
            "symbol": "EURUSD",
            "timestamp": 1272540251000,
            "tp": 0.0,
            "volume": 0.10,
        }

    @pytest.fixture
    def secound_trading_history_response(self):
        return {
            "close_price": 1.5656,
            "close_time": 1272380947000,
            "close_timeString": 0,
            "closed": 0,
            "cmd": 0,
            "comment": "Web Trader",
            "commission": 0.0,
            "customComment": "Some text",
            "digits": 4,
            "expiration": 0,
            "expirationString": 0,
            "margin_rate": 0.0,
            "offset": 0,
            "open_price": 1.4,
            "open_time": 1272380927000,
            "open_timeString": "Fri Jan 11 10:03:36 CET 2013",
            "order": 7497776,
            "order2": 7497776,
            "position": 7497776,
            "profit": -2196.44,
            "sl": 0.0,
            "storage": -4.46,
            "symbol": "EURUSD",
            "timestamp": 1272540251000,
            "tp": 0.0,
            "volume": 0.10,
        }

    @pytest.fixture
    def expected_close_position_dict(self):
        return {
            "symbol": "EURUSD",
            "order": 1234567,
            "position": 1234567,
            "cmd": 0,
            "volume": 0.10,
            "profit": 2196.44,
            "open_price": 1.4,
            "open_time": 1272380927000,
            "close_price": 1.7256,
            "close_time": 1272380967000,
        }

    @pytest.fixture
    def server_time_response(self):
        return {
            "status": True,
            "returnData": {
                "time": 1392211379731,
                "timeString": "Feb 12, 2014 2:22:59 PM",
            },
        }

    def test_is_close_position_return_dict(
        self,
        close_returned_message,
        first_trading_history_response,
        server_time_response,
    ):
        """
        Tests to see if a function returns a dictionary.
        """
        trading_history_msg = {
            "status": True,
            "returnData": [first_trading_history_response],
        }
        client = MagicMock()
        client.send_n_return.side_effect = [
            close_returned_message,
            server_time_response,
            trading_history_msg,
        ]
        close_position_return = close_position(
            client=client,
            symbol="EURUSD",
            position=1234567,
            volume=0.10,
            cmd=0,
        )
        assert isinstance(close_position_return, dict)

    def test_is_close_position_return_expected_dict(
        self,
        close_returned_message,
        first_trading_history_response,
        server_time_response,
        expected_close_position_dict,
    ):
        """
        Tests to see if a function returns a expected dictionary.
        """
        trading_history_msg = {
            "status": True,
            "returnData": [first_trading_history_response],
        }
        client = MagicMock()
        client.send_n_return.side_effect = [
            close_returned_message,
            server_time_response,
            trading_history_msg,
        ]
        close_position_return = close_position(
            client=client,
            symbol="EURUSD",
            position=1234567,
            volume=0.10,
            cmd=0,
        )
        assert close_position_return == expected_close_position_dict

    def test_is_close_position_return_expected_dict_if_many_transaction(
        self,
        close_returned_message,
        first_trading_history_response,
        secound_trading_history_response,
        server_time_response,
        expected_close_position_dict,
    ):
        """
        Test that returns the appropriate value for multiple
        transactions in history.
        """
        trading_history_msg = {
            "status": True,
            "returnData": [
                first_trading_history_response,
                secound_trading_history_response,
            ],
        }
        client = MagicMock()
        client.send_n_return.side_effect = [
            close_returned_message,
            server_time_response,
            trading_history_msg,
        ]
        close_position_return = close_position(
            client=client,
            symbol="EURUSD",
            position=1234567,
            volume=0.10,
            cmd=0,
        )
        assert close_position_return == expected_close_position_dict


class Test_get_historical_candles:
    """
    Tests of the function downloading historical candles.
    """
    @pytest.fixture
    def server_time_response(self):
        return 1392211379731

    @pytest.fixture
    def first_candle_history_response(self):
        return {
            "close": 1.0,
            "ctm": 1392211360000,
            "ctmString": "Jan 10, 2014 3:04:00 PM",
            "high": 6.0,
            "low": 0.0,
            "open": 41848.0,
            "vol": 0.0
        }

    @pytest.fixture
    def secound_candle_history_response(self):
        return {
            "close": 1.0,
            "ctm": 1392211350000,
            "ctmString": "Jan 10, 2014 3:04:00 PM",
            "high": 6.0,
            "low": 0.0,
            "open": 41848.0,
            "vol": 0.0
        }

    @pytest.fixture
    def third_candle_history_response(self):
        return {
            "close": 1.0,
            "ctm": 1392000000000,
            "ctmString": "Jan 10, 2014 3:04:00 PM",
            "high": 6.0,
            "low": 0.0,
            "open": 41848.0,
            "vol": 0.0
        }

    def test_get_historical_candles_return_np_array(self,server_time_response,first_candle_history_response):
        """
        Test if funckja correctly returns an array of np.array.
        """
        trading_history_msg = {
            "status": True,
            "returnData": {
                "digits": 4,
                "rateInfos": [first_candle_history_response]
            }
        }
        client = MagicMock()
        client.send_n_return.return_value = trading_history_msg
        with patch(
            "api.commands.get_server_time", return_value=server_time_response):
            historical_data = get_historical_candles(client=client,symbol="EURUSD",shift=60)
            assert isinstance(historical_data, np.ndarray)