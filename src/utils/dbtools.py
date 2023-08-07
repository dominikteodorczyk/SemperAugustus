"""
Database management tools
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
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from settings import DataBases


def create_specific_transaction_save_model(table_name: str):
    class Base(DeclarativeBase):
        pass

    class TrasactionRecord(Base):
        __tablename__ = table_name
        position = Column(
            "position", Integer, primary_key=True, nullable=False
        )
        symbol = Column("symbol", String)
        order = Column("order", Integer)
        cmd = Column("cmd", Integer)
        volume = Column("volume", Float)
        profit = Column("profit", Float)
        open_price = Column("open_price", Float)
        open_time = Column("open_time", Integer)
        close_price = Column("close_price", Float)
        close_time = Column("close_time", Integer)

    return TrasactionRecord


class TrasactionSave:
    def __init__(self, symbol):
        self.symbol = symbol
        self.engine = create_engine(
            f"sqlite:///{DataBases().transactions}", echo=True
        )
        self.session = sessionmaker(bind=self.engine)()
        self.metadata = MetaData()

        self.check_n_create()

    def create_symbol_table(self):
        Table(
            self.symbol,
            self.metadata,
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
        self.metadata.create_all(self.engine)

    def check_n_create(self):
        if not inspect(self.engine).has_table(self.symbol):
            self.create_symbol_table()

    def add(self, trade):
        model = create_specific_transaction_save_model(self.symbol)
        transaction = model(
            position=trade["position"],
            symbol=trade["symbol"],
            order=trade["order"],
            cmd=trade["cmd"],
            volume=trade["volume"],
            profit=trade["profit"],
            open_price=trade["open_price"],
            open_time=trade["open_time"],
            close_price=trade["close_price"],
            close_time=trade["close_time"],
        )
        self.session.add(transaction)
        self.session.commit()
