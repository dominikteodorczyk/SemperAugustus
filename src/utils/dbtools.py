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
    """
    Creates a specific data model for existing tables that conform
    to the symbol.

    Returns:
        model object
    """

    class Base(DeclarativeBase):
        """
        The Declarative Mapping is the typical way that mappings are
        constructed in modern SQLAlchemy. More:
        https://docs.sqlalchemy.org/en/20/orm/
        """

    class TrasactionRecord(Base):
        """
        Transaction data model  together with the defined table name.
        """

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
    """
    A class representing a transaction saver.

    This class provides functionality to save transactions for a given symbol
    into a SQLite database using SQLAlchemy.

    Args:
        symbol (str): The symbol associated with the transactions.

    Attributes:
        symbol (str): The symbol associated with the transactions.
        engine (Engine): The SQLAlchemy engine object for the database
            connection.
        session (Session): The SQLAlchemy session object for database
            interactions.
        metadata (MetaData): The SQLAlchemy metadata object for table
            and schema definitions.

    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.engine = create_engine(
            f"sqlite:///{DataBases().transactions}", echo=True
        )
        self.session = sessionmaker(bind=self.engine)()
        self.metadata = MetaData()

        self.check_n_create()

    def create_symbol_table(self):
        """
        Method that creates table.
        """
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
        """
        This method checks if a table with the specified symbol name exists
        in the database. If not, it creates the table using the defined
        metadata.
        """
        if not inspect(self.engine).has_table(self.symbol):
            self.create_symbol_table()

    def add(self, trade):
        """
        This method adds a new trade record to the database for the
        specified symbol. The trade information is passed as a dictionary
        containing the trade details.

        Args:
            trade (dict): A dictionary containing trade details with
                the following keys:
                - "position" (int):  The position number of the trade.
                - "symbol" (str): The symbol associated with the trade.
                - "order" (int): The order number of the trade.
                - "cmd" (int): The command identifier for the trade.
                - "volume" (float): The volume of the trade.
                - "profit" (float): The profit earned from the trade.
                - "open_price" (float): The opening price of the trade.
                - "open_time" (int): The timestamp (Unix epoch) when the
                    trade was opened.
                - "close_price" (float): The closing price of the trade.
                - "close_time" (int): The timestamp (Unix epoch) when the
                    trade was closed.
        """
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
