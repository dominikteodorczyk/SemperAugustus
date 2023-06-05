"""
Module that controls the session and technical parameters of the value.
"""



class AssetTechnicalController():
    """
    Manages the technical aspects of a trading session. The facility monitors
    liquidity and spreads on a given currency to catch probable malfunctions
    of the Market Maker trading platform. It also provides data for models
    that calculate risk

    Args:
        symbol (str): A symbol associated with the session.

    Attributes:
        symbol (str): A symbol associated with the session.
    """

    def __init__(self, symbol:str) -> None:
        self.symbol = symbol

    def run(self):
        pass

