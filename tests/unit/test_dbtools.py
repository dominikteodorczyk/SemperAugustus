"""
Testing database tools
"""

import pytest
from settings import DataBases
from unittest.mock import Mock, patch
from utils.dbtools import (
    create_specific_transaction_save_model,
    TrasactionSave,
)


class Test_create_specific_transaction_save_model:
    """
    Test class of the function create_specific_transaction_save_model
    designed to modify the TrasactionRecord object's __tablename__ attribute
    according to the symbol of the data to be saved
    """

    @pytest.fixture
    def mock_sqlalchemy(self):
        base = Mock()
        base.metadata = Mock()
        # session = Mock()
        # create_engine = Mock(return_value=session)

    @pytest.fixture
    def symbol(self):
        return "EURUSD"

    def test_model_connect_with_right_table(self, symbol):
        """
        Test whether the TransactionRecord model selects tables as
        declared in the function (should be the same).
        """
        model = create_specific_transaction_save_model(symbol)
        assert model.__tablename__ == symbol

    @pytest.mark.parametrize(
        "atribut",
        [
            "__tablename__",
            "symbol",
            "order",
            "cmd",
            "volume",
            "profit",
            "open_price",
            "open_time",
            "close_price",
            "close_time",
        ],
    )
    def test_created_table_is_correct(self, symbol, atribut):
        """
        Checking that the table storing data on transactions has the correct
        columns i.e: "symbol", "order", "cmd", "volume", "profit",
        "open_price", "open_time", "close_price", "close_time".
        """
        model = create_specific_transaction_save_model(symbol)
        assert hasattr(model, atribut)

class Test_TrasactionSave:

    @pytest.fixture
    def mock_create_specific_transaction_save_model(self):
        return Mock(return_value=Mock())

    @pytest.fixture
    def mock_sqlalchemy(self):
        mock_create_engine = Mock()
        mock_sessionmaker = Mock()
        mock_metadata = Mock()
        mock_inspect = Mock()
        with patch('src.utils.dbtools.create_engine', mock_create_engine), \
            patch('src.utils.dbtools.sessionmaker', mock_sessionmaker), \
            patch('src.utils.dbtools.MetaData', mock_metadata), \
            patch('src.utils.dbtools.inspect', mock_inspect):
            yield mock_create_engine, mock_sessionmaker, mock_metadata, mock_inspect
