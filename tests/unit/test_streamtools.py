"""
Check the XTBClient of XTB API is valid.
"""

from unittest.mock import Mock, MagicMock, patch
import pytest
import numpy as np
from api.client import XTBClient, stream_session_simulator
from api.streamtools import WalletStream, PositionObservator, DataStream


class Test_WalletStream:
    """
    WalletStream object test class
    """

    @pytest.fixture
    def event_duration(self):
        """
        stream duration definition
        """
        return 5

    @pytest.fixture
    def event(self, event_duration):
        """
        Definition of a stream data duration event using the WalletStream
        object under test subscribing to and ad-reading the wallet balance
        data sent by the API using a decorator that simulates
        stream sessions
        """
        return stream_session_simulator(event_duration)(WalletStream)

    @pytest.fixture
    def mock_xtb_client(self):
        """
        Creating a mockup for XTBClient
        """
        client = MagicMock()
        yield client

    @pytest.fixture
    def mock_xtb_stream_client(self):
        """
        Creating a mockup for XTBClient
        """
        client = MagicMock()
        client.stream_sesion_id = "12345"
        client.connection_stream = True
        yield client

    @pytest.fixture
    def balance_msg(self):
        """
        Balance msg from API for tests
        """
        return {
            "command": "balance",
            "data": {
                "balance": 9992.68,
                "margin": 148.08,
                "equityFX": 9992.23,
                "equity": 9992.23,
                "marginLevel": 6747.86,
                "marginFree": 9844.15,
                "credit": 0.0,
                "stockValue": 0.0,
                "stockLock": 0.0,
                "cashStockValue": 0.0,
            },
        }

    @pytest.fixture
    def balance_array(self):
        """
        Expected balance array from API msg for tests
        """
        return np.array(
            [
                9992.68,
                148.08,
                9992.23,
                9992.23,
                6747.86,
                9844.15,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        )

    def test_walletstream_is_having_api(self):
        """
        Api should be an object of class XTBClient (passed to
        functionfrom wrapper)
        """
        object = WalletStream()
        assert type(object.client) is XTBClient

    @pytest.mark.xfail(
        reason="API sometimes failed to send data during stream"
    )
    def test_walletstream_is_returns_a_numpy_array(self, event):
        """
        Object should store numpy array in attribute
        """
        results = event()
        assert type(results[0]["balance"]) is np.ndarray

    @pytest.mark.xfail(
        reason="API sometimes failed to send data during stream"
    )
    def test_walletstream_is_returns_a_ten_parameters_in_array(self, event):
        """
        API will send a portfolio balance consisting of 10 parameters
        """
        results = event()
        assert np.shape(results[0]["balance"])[0] == 10

    def test_walletstream_is_writing_message_to_balance_array(
        self, mock_xtb_client, balance_msg, balance_array
    ):
        """
        Checking whether the balance stream message was processed correctly
        """
        wallet_stream = WalletStream()
        wallet_stream.client = mock_xtb_client
        wallet_stream.client.stream_read.return_value = balance_msg
        wallet_stream.read_stream()
        assert np.array_equal(wallet_stream.balance, balance_array)

    def test_walletstream_is_not_writing_message_to_balance(
        self, mock_xtb_client
    ):
        """
        Test whether the read_strem method writes balance-only data
        """
        wallet_stream = WalletStream()
        wallet_stream.client = mock_xtb_client
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
                "vol": 0.0,
            },
        }
        wallet_stream.client.stream_read.return_value = mock_message
        wallet_stream.read_stream()
        assert np.array_equal(wallet_stream.balance, np.array([]))


class Test_PositionObservator:
    """
    PositionObservator object test class
    """

    @pytest.fixture
    def mock_xtb_client(self):
        """
        Creating a mockup for client
        """
        client = MagicMock()
        yield client

    @pytest.fixture
    def event_client(self):
        """
        Creating a fixture for XTBClient
        """
        return XTBClient("DEMO")

    @pytest.fixture
    def event_order_no(self):
        """
        Creating a fixture for order no
        """
        return 100000

    @pytest.fixture
    def event_symbol(self):
        """
        Creating a fixture for symbol
        """
        return "EURUSD"

    @pytest.fixture
    def mock_position_obs(self, mock_xtb_client, event_order_no, event_symbol):
        """
        Creating a mockup for PositionObservator
        """
        return PositionObservator(
            client=mock_xtb_client,
            symbol=event_symbol,
            order_no=event_order_no,
        )

    @pytest.fixture
    def price_msg(self):
        """
        Creating fixture of price msg from API
        """
        return {
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
                "timestamp": 1272529161605,
            },
        }

    @pytest.fixture
    def price_array(self):
        """
        Creating fixture of expected price array
        """
        return np.array(
            [
                [
                    4000.0,
                    15000,
                    4000.0,
                    16000,
                    4000.0,
                    0,
                    3500.0,
                    0,
                    0.000003,
                    0.00042,
                    1272529161605,
                ]
            ]
        )

    @pytest.fixture
    def candle_msg(self):
        """
        Creating fixture of candle msg from API
        """
        return {
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
                "vol": 0.0,
            },
        }

    @pytest.fixture
    def candle_array(self):
        """
        Creating fixture of expected candle
        """
        return np.array(
            [
                [
                    4.1849,
                    1378369375000,
                    4.1854,
                    4.1848,
                    4.1848,
                    2,
                    0.0,
                ]
            ]
        )

    @pytest.fixture
    def candle_array_5_minutes(self):
        """
        Creating fixture of calculated candle 5M
        """
        return np.array(
            [
                [
                    4.1849,
                    1378369375000,
                    4.1854,
                    4.1848,
                    4.1848,
                    10,
                    0.0,
                ]
            ]
        )

    @pytest.fixture
    def candle_array_15_minutes(self):
        """
        Creating fixture of calculated candle 15M
        """
        return np.array(
            [
                [
                    4.1849,
                    1378369375000,
                    4.1854,
                    4.1848,
                    4.1848,
                    30,
                    0.0,
                ]
            ]
        )

    @pytest.fixture
    def profit_msg(self, event_order_no):
        """
        Creating fixture of profit msg from API
        """
        return {
            "command": "profit",
            "data": {
                "order": 7497776,
                "order2": event_order_no,
                "position": 7497776,
                "profit": 7076.52,
            },
        }

    @pytest.fixture
    def profit(self):
        """
        Creating fixture of expected profit
        """
        return 7076.52

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
    def test_PositionObservator_have_right_client_attribut(
        self, event_symbol, event_order_no, atribut
    ):
        """
        A test to see if a class object, when initialized, has a set of
        defined attributes
        """
        client = XTBClient("DEMO")
        assert (
            hasattr(
                PositionObservator(
                    client=client, symbol=event_symbol, order_no=event_order_no
                ),
                atribut,
            )
            is True
        )

    @pytest.mark.parametrize(
        "atribut, expected",
        [("symbol", "EURUSD"), ("order_no", 100000), ("profit", 0.0)],
    )
    def test_PositionObservator_have_values_of_attribut_after_init(
        self, event_client, atribut, expected
    ):
        """
        Test to check default attribute values after initialization
        (should be the same)
        """
        client = event_client
        assert (
            PositionObservator(
                client=client, symbol="EURUSD", order_no=100000
            ).__getattribute__(atribut)
            == expected
        )

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("curent_price", np.empty(shape=[0, 11])),
            ("minute_1", np.empty(shape=[0, 7])),
            ("minute_5", np.empty(shape=[0, 7])),
            ("minute_15", np.empty(shape=[0, 7])),
            ("minute_1_5box", np.empty(shape=[0, 7])),
            ("minute_5_15box", np.empty(shape=[0, 7])),
        ],
    )
    def test_PositionObservator_have_values_of_matrix_attributs_after_init(
        self, event_client, atribut, expected
    ):
        """
        Test to check default attribute values after initialization
        (should be the same)
        """
        client = event_client
        assert np.array_equal(
            PositionObservator(
                client=client, symbol="EURUSD", order_no=100000
            ).__getattribute__(atribut),
            expected,
        )

    def test_read_stream_is_writing_price_msg_to_curent_price_atrib(
        self, mock_position_obs, price_msg, price_array
    ):
        """
        The test checks whether the stream information about the current
        price of a stock is assigned to the curent_price attribute
        """
        mock_position_obs.client.stream_read.return_value = price_msg
        mock_position_obs.read_stream()
        expected_curent_price = price_array
        assert np.array_equal(
            mock_position_obs.curent_price, expected_curent_price
        )

    def test_read_stream_is_not_writing_candle_msg_to_curent_price_atrib(
        self, mock_position_obs, candle_msg
    ):
        """
        The test checks whether the stream information about not the current
        price of a stock is not assigned to the curent_price attribute
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        mock_position_obs.read_stream()
        expected_curent_price = np.empty(shape=[0, 11])
        assert np.array_equal(
            mock_position_obs.curent_price, expected_curent_price
        )

    def test_read_stream_writing_profit_msg_to_profit_atrib(
        self, mock_position_obs, profit_msg, profit
    ):
        """
        The test checks whether the stream information about not the current
        profit of a stock is not assigned to the profit attribute
        """
        mock_position_obs.client.stream_read.return_value = profit_msg
        mock_position_obs.read_stream()
        expected_profit = profit
        assert np.array_equal(mock_position_obs.profit, expected_profit)

    def test_read_stream_is_not_writing_candle_msg_to_profit_atrib(
        self, mock_position_obs, candle_msg
    ):
        """
        The test checks whether the stream information about not the current
        profit of a stock is not assigned to the profit attribute
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        mock_position_obs.read_stream()
        expected_profit = 0.0
        assert np.array_equal(mock_position_obs.profit, expected_profit)

    def test_read_stream_writing_candle_msg_to_minute_1_atrib(
        self, mock_position_obs, candle_msg, candle_array
    ):
        """
        The test checks whether the stream information about not the current
        # profit of a stock is not assigned to the profit attribute
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        mock_position_obs.read_stream()
        expected_minute_1 = candle_array
        assert np.array_equal(mock_position_obs.minute_1, expected_minute_1)

    def test_read_stream_is_not_writing_price_msg_to_minute_1_atrib(
        self, mock_position_obs, price_msg
    ):
        """
        Test to see if the price message is not assigned to an
        attribute minute_1
        """
        mock_position_obs.client.stream_read.return_value = price_msg
        mock_position_obs.read_stream()
        expected_minute_1 = np.empty(shape=[0, 7])
        assert np.array_equal(mock_position_obs.minute_1, expected_minute_1)

    @pytest.mark.parametrize(
        "M1_candles_no, expected_minute_1_5box_shape", [(1, 1), (2, 2), (3, 3)]
    )
    def test_make_more_candles_agregate_1M_candles_to_minute_1_5box(
        self,
        mock_position_obs,
        candle_msg,
        M1_candles_no,
        expected_minute_1_5box_shape,
    ):
        """
        Test to see if 1 minute candles aggregate to contener minute_1_5box
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(M1_candles_no):
            mock_position_obs.read_stream()
        assert (
            np.shape(mock_position_obs.minute_1_5box)[0]
            == expected_minute_1_5box_shape
        )

    def test_make_more_candles_five_1M_candles_make_minute_5_candle(
        self, mock_position_obs, candle_msg
    ):
        """
        Test to see if a 5 minute candle will form after sending
        five 1 minute candles
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(5):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert np.shape(mock_position_obs.minute_5)[0] == 1

    def test_make_more_candles_after_five_1M_candles_minute_1_5box_is_empty(
        self, mock_position_obs, candle_msg
    ):
        """
        Test whether the contender for 1-minute candles will be cleared
        after calculating 5-minute candles
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(5):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert np.shape(mock_position_obs.minute_1_5box)[0] == 0

    def test_make_more_candles_calc_right_5_min_candle(
        self, mock_position_obs, candle_msg, candle_array_5_minutes
    ):
        """
        Correctness of calculation of 5 miute candle from 1 minute candles
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(5):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert np.array_equal(
            mock_position_obs.minute_5, candle_array_5_minutes
        )

    @pytest.mark.parametrize(
        "M1_candles_no, expected_minute_5_15box_shape",
        [(4, 0), (9, 1), (14, 2)],
    )
    def test_make_more_candles_agregate_5M_candles_to_minute_5_15box(
        self,
        mock_position_obs,
        candle_msg,
        M1_candles_no,
        expected_minute_5_15box_shape,
    ):
        """
        Test to see if 5-minute candles are saved in the 5-minute candle
        container for the 15-minute candle arrangement
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(M1_candles_no):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert (
            np.shape(mock_position_obs.minute_5_15box)[0]
            == expected_minute_5_15box_shape
        )

    def test_make_more_candles_after_three_5M_candles_delete_minute_5_15box(
        self, mock_position_obs, candle_msg
    ):
        """
        Test to see if three 5-minute nets clear the 5-minute
        candle contender
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(15):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert np.shape(mock_position_obs.minute_5_15box)[0] == 0

    def test_make_more_candles_after_three_5M_make_minute_15_candle(
        self, mock_position_obs, candle_msg
    ):
        """
        Test to see if three 5-minute nets create a 15-minute candle
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(15):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert np.shape(mock_position_obs.minute_15)[0] == 1

    def test_make_more_candles_agregate_minute_15_candle_right(
        self, mock_position_obs, candle_msg, candle_array_15_minutes
    ):
        """
        Checking the correctness of the calculation of the 15-minute
        candle on the basis of 5-minute candles
        """
        mock_position_obs.client.stream_read.return_value = candle_msg
        for i in range(15):
            mock_position_obs.read_stream()
            mock_position_obs.make_more_candles()
        assert np.array_equal(
            mock_position_obs.minute_15, candle_array_15_minutes
        )


class Test_DataStream:
    @pytest.fixture
    def mock_xtb_client(self):
        # Creating a mockup for XTBClient
        client = MagicMock()
        client.connection_stream = True
        yield client

    @pytest.fixture
    def event_symbol(self):
        """
        Creating a fixture for symbol
        """
        return "EURUSD"

    @pytest.fixture
    def mock_data_stream(self, event_symbol, mock_xtb_client):
        """
        Creating a mockup for DataStream
        """
        data_stream = DataStream(event_symbol)
        data_stream.client = mock_xtb_client
        return data_stream

    @pytest.fixture
    def price_msg(self):
        """
        Creating fixture of price msg from API
        """
        return {
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
                "timestamp": 1272529161605,
            },
        }

    @pytest.fixture
    def price_array(self):
        """
        Creating fixture of expected price array for price_msg
        """
        return np.array(
            [
                [
                    4000.0,
                    15000,
                    4000.0,
                    16000,
                    4000.0,
                    0,
                    3500.0,
                    0,
                    0.000003,
                    0.00042,
                    1272529161605,
                ]
            ]
        )

    @pytest.fixture
    def price_msg2(self):
        """
        Creating secound fixture of price msg from API
        """
        return {
            "command": "tickPrices",
            "data": {
                "ask": 5000.0,
                "askVolume": 15000,
                "bid": 4000.0,
                "bidVolume": 16000,
                "high": 7000.0,
                "level": 0,
                "low": 3500.0,
                "quoteId": 0,
                "spreadRaw": 0.000003,
                "spreadTable": 0.00042,
                "symbol": "EURUSD",
                "timestamp": 1272529161605,
            },
        }

    @pytest.fixture
    def candle_msg_test(self):
        """
        Creating fixture of candle msg from API
        """
        return {
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
                "vol": 0.0,
            },
        }

    @pytest.fixture
    def candle_array(self):
        """
        Creating fixture of expected candle for candle_msg_test
        """
        return np.array(
            [
                [
                    4.1849,
                    1378369375000,
                    4.1854,
                    4.1848,
                    4.1848,
                    0.0,
                ]
            ]
        )

    @pytest.fixture
    def candle_msg_test2(self):
        """
        Creating secound fixture of candle msg from API
        """
        return {
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
                "vol": 1.0,
            },
        }

    @pytest.mark.parametrize(
        "atribut",
        [
            "client",
            "symbol",
            "server_time",
            "tick_msg",
            "candle_msg",
            "symbols_price",
            "symbols_last_1M",
        ],
    )
    def test_data_stream_attributes(self, mock_data_stream, atribut):
        """
        Implementation test of required attributes
        """
        assert hasattr(mock_data_stream, atribut) is True

    @pytest.mark.parametrize(
        "atribut, expected",
        [
            ("symbol", "EURUSD"),
            ("server_time", None),
            ("tick_msg", {}),
            ("candle_msg", {}),
            ("symbols_price", np.empty(shape=[0, 11])),
            ("symbols_last_1M", np.empty(shape=[0, 7])),
        ],
    )
    def test_data_stream_attributes_default_atributes(
        self, mock_data_stream, atribut, expected
    ):
        """
        Implementation test of required attributes with
        default defined values
        """
        assert np.array_equal(
            mock_data_stream.__getattribute__(atribut), expected
        )

    def test_read_stream_messages_write_candle_msg_to_candle_msg_atrib(
        self, mock_data_stream, candle_msg_test
    ):
        """
        Test to check if candle api message is stored in candle_msg attribute
        """
        mock_data_stream.is_connected = Mock(side_effect=iter([True, False]))
        mock_data_stream.client.stream_read = Mock(
            side_effect=iter([candle_msg_test])
        )
        mock_data_stream.read_stream_messages()
        assert mock_data_stream.candle_msg == candle_msg_test

    def test_read_stream_messages_overwrite_candle_msg_in_candle_msg_atrib(
        self, mock_data_stream, candle_msg_test, candle_msg_test2
    ):
        """
        Test to see if candle api messages are overwritten in
        candle_msg attribute
        """
        mock_data_stream.is_connected = Mock(
            side_effect=iter([True, True, False])
        )
        mock_data_stream.client.stream_read = Mock(
            side_effect=iter([candle_msg_test, candle_msg_test2])
        )
        mock_data_stream.read_stream_messages()
        assert mock_data_stream.candle_msg == candle_msg_test2

    def test_read_stream_messages_write_tickPrices_msg_to_tick_msg_atrib(
        self, mock_data_stream, price_msg
    ):
        """
        Is the message from the api about the price written to
        the tick_msg attribute
        """
        mock_data_stream.is_connected = Mock(side_effect=iter([True, False]))
        mock_data_stream.client.stream_read = Mock(
            side_effect=iter([price_msg])
        )
        mock_data_stream.read_stream_messages()
        assert mock_data_stream.tick_msg == price_msg

    def test_read_stream_messages_overwrite_tickPrices_msg_in_tick_msg_atrib(
        self, mock_data_stream, price_msg, price_msg2
    ):
        """
        Test to see if tick price api messages are overwritten in
        tick_msg attribute
        """
        mock_data_stream.is_connected = Mock(
            side_effect=iter([True, True, False])
        )
        mock_data_stream.client.stream_read = Mock(
            side_effect=iter([price_msg, price_msg2])
        )
        mock_data_stream.read_stream_messages()
        assert mock_data_stream.tick_msg == price_msg2

    def test_read_prices_convert_tick_msg_to_symbols_price(
        self, mock_data_stream, price_msg, price_array
    ):
        """
        Test if the price message is correctly converted to the
        symbols_price class attribute
        """
        mock_data_stream.is_connected = Mock(
            side_effect=iter([True, True, False])
        )
        with patch.object(mock_data_stream, "tick_msg", new=price_msg):
            mock_data_stream.read_prices()
        assert np.array_equal(mock_data_stream.symbols_price, price_array)

    def test_read_prices_not_convert_candle_msg_to_symbols_price(
        self, mock_data_stream, candle_msg_test
    ):
        """
        Test if the candle message is not converted to the
        symbols_price class attribute
        """
        mock_data_stream.is_connected = Mock(
            side_effect=iter([True, True, False])
        )
        with patch.object(mock_data_stream, "candle_msg", new=candle_msg_test):
            mock_data_stream.read_prices()
        assert np.array_equal(
            mock_data_stream.symbols_price, np.empty(shape=[0, 11])
        )

    def test_read_last_1M_convert_candle_msg_to_symbols_last_1M(
        self, mock_data_stream, candle_msg_test, candle_array
    ):
        """
        Test if the candle message is  converted to the
        symbols_last_1M class attribute
        """
        mock_data_stream.is_connected = Mock(
            side_effect=iter([True, True, False])
        )
        with patch.object(mock_data_stream, "candle_msg", new=candle_msg_test):
            mock_data_stream.read_last_1M()
        assert np.array_equal(mock_data_stream.symbols_last_1M, candle_array)
