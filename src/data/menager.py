"""
Menager danych umożliwiający zasilanie oraz pobieranie danych historycznych
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    MetaData,
    Table,
    inspect,
)
from sqlalchemy.orm import sessionmaker
from settings import DataBases


class TrasactionRepository:
    def __init__(self, symbol):
        self.symbol = symbol
        self.engine = create_engine(f"sqlite:///{DataBases().transactions}")
        self.session = sessionmaker(bind=self.engine)

        if not inspect(self.engine).has_table(self.symbol):
            metadata = MetaData()
            Table(
                self.symbol,
                metadata,
                Column("position", Integer, primary_key=True, nullable=False),
                Column("symbol", String),
                Column("order", Integer),
                Column("cmd", Integer),
                Column("volume", Float),
                Column("profit", Float),
                Column("open_price", Float),
                Column("open_time", Integer),
                Column("close_price", Float),
                Column("close_time", Integer),
            )
            metadata.create_all(self.engine)
