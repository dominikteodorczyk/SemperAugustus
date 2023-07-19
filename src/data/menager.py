"""
Menager danych umożliwiający zasilanie oraz pobieranie danych historycznych
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DataBases


class Transaction(declarative_base()):
    __tablename__ = "transactions"

    position = Column(Integer, primary_key=True)
    symbol = Column(String)
    order = Column(Integer)
    cmd = Column(Integer)
    volume = Column(Float)
    profit = Column(Float)
    open_price = Column(Float)
    open_time = Column(Integer)
    close_price = Column(Float)
    close_time = Column(Integer)

    def __repr__(self):
        return f"<Transaction(position='{self.position}', symbol='{self.symbol}', order='{self.order}', cmd='{self.cmd}', volume='{self.volume}', profit='{self.profit}', open_price='{self.open_price}', open_time='{self.open_time}', close_price='{self.close_price}', close_time='{self.close_time}')>"

class TrasactionRepository:

    DB_URL = f'sqlite:///{DataBases().transactions}'

    def __init__(self):
        self.engine = create_engine(TrasactionRepository.DB_URL)
        self.session = sessionmaker(bind=self.engine)

    def create_transaction(self, transaction_data):
        symbol = transaction_data['symbol']
        symbol_table_name = f"table_{symbol}"

        # Sprawdzamy, czy tabela dla danego symbolu już istnieje
        if not symbol in self._engine.table_names():
            self.create_symbol_table(symbol_table_name)
        try:
            transaction = Transaction(**transaction_data)
            self.session.add(transaction)
            self.session.commit()
            return transaction
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()

    def create_symbol_table(self, table_name):
        class SymbolTransaction(declarative_base()):
            __tablename__ = table_name

            position = Column(Integer, primary_key=True)
            symbol = Column(String)
            order = Column(Integer)
            cmd = Column(Integer)
            volume = Column(Float)
            profit = Column(Float)
            open_price = Column(Float)
            open_time = Column(Integer)
            close_price = Column(Float)
            close_time = Column(Integer)

        SymbolTransaction.__table__.create(self.engine)

