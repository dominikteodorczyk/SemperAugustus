"""
Check the XTBClient of XTB API is valid.
"""

import pytest
import itertools
from unittest.mock import MagicMock
import numpy as np
from api.client import XTBClient, stream_session_simulator
from api.streamtools import WalletStream, PositionObservator


class Test_WalletStream:
    # stream duration definition
    @pytest.fixture
    def event_duration(self):
        return 5

    # definition of a stream data duration event using the WalletStream object
    # under test subscribing to and ad-reading the wallet balance data sent by
    # the API using a decorator that simulates stream sessions
    @pytest.fixture
    def event(self, event_duration):
        # returns[0] = {api:api, balance:balance},
        # returns[1] = args,
        # returns[2] = kwargs
        return stream_session_simulator(event_duration)(WalletStream)

    @pytest.fixture
    def mock_xtb_client(self):
        # Creating a mockup for XTBClient
        client = MagicMock()
        yield client

    @pytest.fixture
    def mock_xtb_stream_client(self):
        # Creating a mockup for XTBClient
        client = MagicMock()
        client.stream_sesion_id = "12345"
        client.connection_stream = True
        yield client

    def test_walletstream_is_having_api(self, event):
        object = WalletStream()
        assert type(object.client) is XTBClient
        # api should be an object of class XTBClient
        # (passed to functionfrom wrapper)

    @pytest.mark.xfail(
        reason="API sometimes failed to send data during stream"
    )
    def test_walletstream_is_returns_a_numpy_array(self, event):
        results = event()
        assert (
            type(results[0]["balance"]) is np.ndarray
        )  # object should store numpy array in attribute

    @pytest.mark.xfail(
        reason="API sometimes failed to send data during stream"
    )
    def test_walletstream_is_returns_a_ten_parameters_in_array(self, event):
        results = event()
        assert (
            np.shape(results[0]["balance"])[0] == 10
        )  # API will send a portfolio balance consisting of 10 parameters

    def test_walletstream_is_writing_message_to_balance_array(self, mock_xtb_client):
        # Creating a WalletStream instance with a mock XTBClient
        wallet_stream = WalletStream()
        wallet_stream.client = mock_xtb_client
        # Preparing data to be returned by the mock XTBClient.stream_read method
        mock_message = {
            'command': 'balance',
            'data': {
                'balance': 9992.68,
                'margin': 148.08,
                'equityFX': 9992.23,
                'equity': 9992.23,
                'marginLevel': 6747.86,
                'marginFree': 9844.15,
                'credit': 0.0,
                'stockValue': 0.0,
                'stockLock': 0.0,
                'cashStockValue': 0.0
            }
        }
        # Setting the behavior of mock XTBClient.read_stream
        wallet_stream.client.stream_read.return_value = mock_message
        # Calling the read_stream method
        wallet_stream.read_stream()
        # Checking whether the balance stream message was processed correctly
        expected_balance = np.array(
            [9992.68, 148.08, 9992.23, 9992.23, 6747.86, 9844.15, 0.0, 0.0, 0.0, 0.0]
        )
        assert np.array_equal(wallet_stream.balance, expected_balance)

    def test_walletstream_is_not_writing_message_to_balance(self, mock_xtb_client):
        # Test whether the read_strem method writes balance-only data
        # Creating a WalletStream instance with a mock XTBClient
        wallet_stream = WalletStream()
        wallet_stream.client = mock_xtb_client
        # Preparing data to be returned by the mock XTBClient.stream_read method
        mock_message = {
            "command": "candle",
            "data": {
                "close": 4.1849,
                "ctm": 1378369375000,
                "ctmString": "Sep 05, 2013 10:22:55 AM",
                "high": 4.1854,
                "low": 4.1848,
                "open": 4.1848,
                "quoteId": 2,
                "symbol": "EURUSD",
                "vol": 0.0
            }
        }
        # Setting the behavior of mock XTBClient.read_stream
        wallet_stream.client.stream_read.return_value = mock_message
        # Calling the read_stream method
        wallet_stream.read_stream()
        # Checking whether the balance stream message was processed correctly
        expected_balance = np.array([])
        assert np.array_equal(wallet_stream.balance, expected_balance)

class Test_PositionObservator:

    @pytest.fixture
    def mock_xtb_client(self):
        # Creating a mockup for XTBClient
        client = MagicMock()
        yield client

    @pytest.fixture
    def event_client(self):
        return XTBClient("DEMO")

    @pytest.fixture
    def event_order_no(self):
        return 100000

    @pytest.fixture
    def event_symbol(self):
        return "EURUSD"

    @pytest.mark.parametrize(
        "atribut",
        [
            "client",
            "symbol",
            "order_no",
            "curent_price",
            "profit",
            "minute_1",
            "minute_5",
            "minute_15",
            "minute_1_5box",
            "minute_5_15box",
        ],
    )
    def test_PositionObservator_have_attribut(self, event_symbol, event_order_no, atribut):
        # A test to see if a class object, when initialized, has a set of
        # defined attributes
        client = XTBClient("DEMO")
        assert (
            hasattr(PositionObservator(
              client=client, symbol=event_symbol, order_no=event_order_no), atribut) is True
        )

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("symbol", "EURUSD"),
            ("order_no", 100000),
            ("profit", 0.0)]
    )
    def test_PositionObservator_have_values_of_attribut_after_init(self, event_client, atribut, expected):
        # test to check default attribute values after initialization
        client = event_client
        assert (
            PositionObservator(
                client=client, symbol="EURUSD", order_no=100000).__getattribute__(
                    atribut) == expected
        )# should be the same

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("curent_price",  np.empty(shape=[0, 11])),
            ("minute_1", np.empty(shape=[0, 7])),
            ("minute_5", np.empty(shape=[0, 7])),
            ("minute_15", np.empty(shape=[0, 7])),
            ("minute_1_5box", np.empty(shape=[0, 7])),
            ("minute_5_15box", np.empty(shape=[0, 7]))]
    )
    def test_PositionObservator_have_values_of_matrix_attributs_after_init(self, event_client, atribut, expected):
        # test to check default attribute values after initialization
        client = event_client
        assert (np.array_equal(PositionObservator(
                client=client, symbol="EURUSD", order_no=100000).__getattribute__(
                    atribut), expected)
        )# should be the same

    def test_read_stream_writing_price_msg_to_curent_price_atrib(self,mock_xtb_client):
        # the test checks whether the stream information about the current price of a stock
        # is assigned to the curent_price attribute
        position_obs = PositionObservator(client=XTBClient("DEMO"), symbol="EURUSD", order_no=100000)
        position_obs.client = mock_xtb_client
        # Preparing data to be returned by the mock XTBClient.stream_read method
        mock_message = {
            "command": "tickPrices",
            "data": {
                "ask": 4000.0,
                "askVolume": 15000,
                "bid": 4000.0,
                "bidVolume": 16000,
                "high": 4000.0,
                "level": 0,
                "low": 3500.0,
                "quoteId": 0,
                "spreadRaw": 0.000003,
                "spreadTable": 0.00042,
                "symbol": "EURUSD",
                "timestamp": 1272529161605
            }
        }
        # Setting the behavior of mock XTBClient.read_stream
        position_obs.client.stream_read.return_value = mock_message
        # Calling the read_stream method
        position_obs.read_stream()
        # Checking whether the curent price stream message was processed correctly
        expected_curent_price = np.array(
            [4000.0, 15000, 4000.0, 16000, 4000.0, 0, 3500.0, 0, 0.000003, 0.00042, 1272529161605]
        ).reshape(1, 11)
        assert np.array_equal(position_obs.curent_price, expected_curent_price)

    def test_read_stream_not_writing_price_msg_to_curent_price_atrib(self,mock_xtb_client):
        # the test checks whether the stream information about not the current price of a stock
        # is not assigned to the curent_price attribute
        position_obs = PositionObservator(client=XTBClient("DEMO"), symbol="EURUSD", order_no=100000)
        position_obs.client = mock_xtb_client
        # Preparing data to be returned by the mock XTBClient.stream_read method
        mock_message = {
            "command": "candle",
            "data": {
                "close": 4.1849,
                "ctm": 1378369375000,
                "ctmString": "Sep 05, 2013 10:22:55 AM",
                "high": 4.1854,
                "low": 4.1848,
                "open": 4.1848,
                "quoteId": 2,
                "symbol": "EURUSD",
                "vol": 0.0
            }
        }
        # Setting the behavior of mock XTBClient.read_stream
        position_obs.client.stream_read.return_value = mock_message
        # Calling the read_stream method
        position_obs.read_stream()
        # Checking whether the curent price stream message was processed correctly
        expected_curent_price = np.empty(shape=[0, 11])
        assert np.array_equal(position_obs.curent_price, expected_curent_price)

    def test_read_stream_not_writing_profit_msg_to_profit_atrib(self,mock_xtb_client):
        # the test checks whether the stream information about not the current profit of a stock
        # is not assigned to the profit attribute
        position_obs = PositionObservator(client=XTBClient("DEMO"), symbol="EURUSD", order_no=100000)
        position_obs.client = mock_xtb_client
        # Preparing data to be returned by the mock XTBClient.stream_read method
        mock_message = {
            "command": "candle",
            "data": {
                "close": 4.1849,
                "ctm": 1378369375000,
                "ctmString": "Sep 05, 2013 10:22:55 AM",
                "high": 4.1854,
                "low": 4.1848,
                "open": 4.1848,
                "quoteId": 2,
                "symbol": "EURUSD",
                "vol": 0.0
            }
        }
        # Setting the behavior of mock XTBClient.read_stream
        position_obs.client.stream_read.return_value = mock_message
        # Calling the read_stream method
        position_obs.read_stream()
        # Checking whether the  stream message was processed correctly
        expected_profit = 0.0
        assert np.array_equal(position_obs.profit, expected_profit)