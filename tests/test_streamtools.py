"""
Check the Client of XTB API is valid.
"""

import pytest
from src.api.client import *
from src.api.streamtools import *


class Test_WalletStream:

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
        assert (
            type(results[0]["api"]) is Client
        )  # api should be an object of class Client (passed to function from wrapper)

    @pytest.mark.xfail(reason="API sometimes failed to send data during stream")
    def test_walletstream_is_returns_a_numpy_array(self, event):
        results = event()
        assert (
            type(results[0]["balance"]) is np.ndarray
        )  # object should store numpy array in attribute

    @pytest.mark.xfail(
        reason="API sometimes failed to send data during stream", xfail_strict=True
    )
    def test_walletstream_is_returns_a_ten_parameters_in_array(self, event):
        results = event()
        assert (
            np.shape(results[0]["balance"])[0] is 10
        )  # API will send a portfolio balance consisting of 10 parameters


class Test_AssetBOX:

    # stream duration definition
    @pytest.fixture
    def event_duration(self):
        return 5

    # stream symbol parameters definition
    @pytest.fixture
    def event_symbol(self):
        return "EURUSD"

    # definition of a stream data duration event using the AssetBOX object under test
    # subscribing to and ad-reading the asset parameters data sent by the API using a decorator
    # that simulates stream sessions
    @pytest.fixture
    def event(self, event_duration, event_symbol):
        # returns[0] = {api:api, 'symbol': 'EURUSD', 'open_stream_data_M1': open_stream_data_M1, 'open_stream_data_M5': open_stream_data_M5,
        # 'candle_1M': candle_1M, 'candle_5M': candle_5M, 'candle_15M': candle_15M, 'price': price},
        # returns[1] = args,
        # returns[2] = kwargs
        return stream_session_simulator(event_duration)(AssetObservator)(
            symbol=event_symbol
        )

    @pytest.mark.parametrize(
        "atribut",
        [
            "api",
            "symbol",
            "open_stream_data_M1",
            "open_stream_data_M5",
            "candle_1M",
            "candle_5M",
            "candle_15M",
            "candle_1H",
            "price",
        ],
    )
    def test_AssetBOX_have_attribut(self, event_symbol, atribut):
        # A test to see if a class object, when initialized, has a set of defined attributes
        assert hasattr(AssetObservator(symbol=event_symbol), atribut) is True

    def test_AssetBOX_have_Client_as_api_after_init(self, event_symbol):
        # test to check the correctness of assigning objects to attributes
        api = Client("DEMO")
        api.opensession()
        assert (
            type(AssetObservator(api=api, symbol=event_symbol).api) == Client
        )  # should be the same
        api.closesession()

    def test_AssetBOX_have_event_symbol_as_symbol_after_init(self, event_symbol):
        # test to check the correctness of assigning objects to attributes
        api = Client("DEMO")
        api.opensession()
        assert (
            AssetObservator(api=api, symbol=event_symbol).symbol == event_symbol
        )  # should be the same
        api.closesession()

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("open_stream_data_M1", None),
            ("open_stream_data_M5", None),
            ("candle_1M", None),
            ("candle_5M", None),
            ("candle_15M", None),
            ("candle_1H", None),
            ("price", None),
        ],
    )
    def test_AssetBOX_have_values_of_attribut_after_init(
        self, event_symbol, atribut, expected
    ):
        # test to check default attribute values after ninitialization
        api = Client("DEMO")
        api.opensession()
        assert (
            AssetObservator(api=api, symbol=event_symbol).__getattribute__(atribut)
            == expected
        )  # should be the same
        api.closesession()

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("open_stream_data_M1", True),
            ("open_stream_data_M5", True),
            ("candle_1M", True),
            ("candle_5M", True),
            ("candle_15M", True),
            ("candle_1H", True),
            ("price", True),
        ],
    )
    def test_AssetBOX_get_values_after_stream(self, event, atribut, expected):
        exist = None
        if event[0][atribut]:
            exist = True
        assert exist is expected

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("open_stream_data_M1", True),
            ("open_stream_data_M5", True),
            ("candle_1M", True),
            ("candle_5M", True),
            ("candle_15M", True),
            ("candle_1H", True),
            ("price", True),
        ],
    )
    def test_AssetBOX_get_values_after_stream(self, event, atribut, expected):
        exist = None
        if event[0][atribut]:
            exist = True
        assert exist is expected
