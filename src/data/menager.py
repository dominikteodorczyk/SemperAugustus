"""
Menager danych umożliwiający zasilanie oraz pobieranie danych historycznych
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Transaction(declarative_base()):
    __tablename__ = "transactions"

    position = Column(int)
    symbol = Column(String)
    order = Column(int)
    cmd = Column(int)
    volume = Column(float)
    profit = Column(float)
    open_price = Column(float)
    open_time = Column(int)
    close_price = Column(float)
    close_time = Column(int)

    def __repr__(self):
        return f"<Transaction(position='{self.position}', symbol='{self.symbol}', order='{self.order}', cmd='{self.cmd}', volume='{self.volume}', profit='{self.profit}', open_price='{self.open_price}', open_time='{self.open_time}', close_price='{self.close_price}', close_time='{self.close_time}')>"

