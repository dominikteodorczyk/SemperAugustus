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
    @pytest.fixture
    def mock_sqlalchemy(self):
        base = Mock()
        base.metadata = Mock()
        session = Mock()
        create_engine = Mock(return_value=session)

    @pytest.fixture
    def symbol(self):
        return "EURUSD"

    def test_model_connect_with_right_table(self, symbol):
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
        model = create_specific_transaction_save_model(symbol)
        assert hasattr(model, atribut)

