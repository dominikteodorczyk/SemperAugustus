"""
Check the XTBClient of XTB API is valid.
"""

import pytest
from unittest.mock import MagicMock
import numpy as np
from api.client import XTBClient, stream_session_simulator
from api.streamtools import WalletStream


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
        # FIXME: Tworzenie mocka dla XTBClient
        client = MagicMock()
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

    def test_walletstream_is_overwriting_balance_while_stream(self, mock_xtb_client):
        # Test whether the read_strem method writes balance-only data
        # Creating a WalletStream instance with a mock XTBClient
        wallet_stream = WalletStream()
        wallet_stream.client = mock_xtb_client
        # Preparing data to be returned by the mock XTBClient.stream_read method
        mock_message = [
        {
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
        },
        {
            'command': 'balance',
            'data': {
                'balance': 9998.68,
                'margin': 146.08,
                'equityFX': 9942.23,
                'equity': 9292.23,
                'marginLevel': 6767.86,
                'marginFree': 9843.15,
                'credit': 1.24,
                'stockValue': 0.0,
                'stockLock': 0.0,
                'cashStockValue': 12.0
            }
        }
    ]
        # Setting the behavior of mock XTBClient.read_stream
        wallet_stream.client.stream_read.side_effect = mock_message
        # Calling the read_stream method
        wallet_stream.stream()
        # Checking that the open_session and subscribe methods were called correctly
        wallet_stream.client.open_session.assert_called_once()
        # Checking whether the balance stream message was processed correctly
        expected_balance = np.array(
            [9998.68, 146.08, 9942.23, 9292.23, 6767.86, 9843.15, 1.24, 0.0, 0.0, 12.0]
        )
        assert np.array_equal(wallet_stream.balance, expected_balance)

# TODO: use the following tests to cosntruct the others.
# @pytest.mark.skip(reason="Class withdrawn / to be rebuilt")
# class Test_AssetBOX:
#     # stream duration definition
#     @pytest.fixture
#     def event_duration(self):
#         return 5

#     # stream symbol parameters definition
#     @pytest.fixture
#     def event_symbol(self):
#         return "EURUSD"

#     # definition of a stream data duration event using the AssetBOX object
#     # under test subscribing to and ad-reading the asset parameters data
#     # sent by the API using a decorator that simulates stream sessions
#     @pytest.fixture
#     def event(self, event_duration, event_symbol):
#         return stream_session_simulator(event_duration)(PositionObservator)(
#             symbol=event_symbol
#         )

#     @pytest.mark.parametrize(
#         "atribut",
#         [
#             "api",
#             "symbol",
#             "open_stream_data_M1",
#             "open_stream_data_M5",
#             "candle_1M",
#             "candle_5M",
#             "candle_15M",
#             "candle_1H",
#             "price",
#         ],
#     )
#     def test_AssetBOX_have_attribut(self, event_symbol, atribut):
#         # A test to see if a class object, when initialized, has a set of
#         # defined attributes
#         assert (
#             hasattr(PositionObservator(symbol=event_symbol), atribut) is True
#         )

#     def test_AssetBOX_have_XTBClient_as_api_after_init(self, event_symbol):
#         # test to check the correctness of assigning objects to attributes
#         api = XTBClient("DEMO")
#         api.opensession()
#         assert (
#             type(PositionObservator(api=api, symbol=event_symbol).api)
#             == XTBClient
#         )  # should be the same
#         api.closesession()

#     def test_AssetBOX_have_event_symbol_as_symbol_after_init(
#         self, event_symbol
#     ):
#         # test to check the correctness of assigning objects to attributes
#         api = XTBClient("DEMO")
#         api.opensession()
#         assert (
#             PositionObservator(api=api, symbol=event_symbol).symbol
#             == event_symbol
#         )  # should be the same
#         api.closesession()

#     @pytest.mark.parametrize(
#         "atribut, expected",
#         [
#             ("open_stream_data_M1", None),
#             ("open_stream_data_M5", None),
#             ("candle_1M", None),
#             ("candle_5M", None),
#             ("candle_15M", None),
#             ("candle_1H", None),
#             ("price", None),
#         ],
#     )
#     def test_AssetBOX_have_values_of_attribut_after_init(
#         self, event_symbol, atribut, expected
#     ):
#         # test to check default attribute values after ninitialization
#         api = XTBClient("DEMO")
#         api.opensession()
#         assert (
#             PositionObservator(
#               api=api, symbol=event_symbol).__getattribute__(
#                 atribut
#             )
#             == expected
#         )  # should be the same
#         api.closesession()

#     @pytest.mark.parametrize(
#         "atribut, expected",
#         [
#             ("open_stream_data_M1", True),
#             ("open_stream_data_M5", True),
#             ("candle_1M", True),
#             ("candle_5M", True),
#             ("candle_15M", True),
#             ("candle_1H", True),
#             ("price", True),
#         ],
#     )
#     def test_AssetBOX_get_values_after_stream(
#           self, event, atribut, expected
#           ):
#         exist = None
#         if event[0][atribut]:
#             exist = True
#         assert exist is expected

#     @pytest.mark.parametrize(
#         "atribut, expected",
#         [
#             ("open_stream_data_M1", True),
#             ("open_stream_data_M5", True),
#             ("candle_1M", True),
#             ("candle_5M", True),
#             ("candle_15M", True),
#             ("candle_1H", True),
#             ("price", True),
#         ],
#     )
#     def test_AssetBOX_get_values_after_stream(
#           self, event, atribut, expected
#           ):
#         exist = None
#         if event[0][atribut]:
#             exist = True
#         assert exist is expected
