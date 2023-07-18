'''
Menager danych umożliwiający zasilanie oraz pobieranie danych historycznych
'''

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

class DataBaseClient:

    def __init__(self) -> None:
