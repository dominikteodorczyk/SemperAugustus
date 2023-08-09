"""
Testing database tools
"""

import pytest
from unittest.mock import Mock
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

    def mock_sqlalchemy(self):
        base = Mock()
        base.metadata = Mock()
        session = Mock()
        create_engine = Mock(return_value=session)

        with pytest.MonkeyPatch().context() as m:
            m.setattr('src.util.dbtools.DeclarativeBase', base)
            m.setattr('src.util.dbtools.create_engine', create_engine)
            m.setattr('src.util.dbtools.sessionmaker', Mock(return_value=session))
            yield base, session