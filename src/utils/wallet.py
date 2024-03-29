"""
Module containing portfolio definitions and algorithms that manage risk
"""

from api.streamtools import WalletStream


class Wallet:
    """
    Portfolio object class, calculating risk and performing money management.
    """

    def __init__(self, symbols) -> None:
        self.symbols = symbols
        self.wallet_stream = WalletStream()
        self.wallet_data = self.wallet_stream.balance
        self.wallet_performace = WalletPerform()
        self.portfolio_risk = PortfolioRiskMenagment()

    def run(self):
        pass


class WalletPerform:
    """
    A class of object that calculates portfolio performance over time
    and risk statistics.
    """

    def __init__(self) -> None:
        pass


class PortfolioRiskMenagment:
    """
    A class of object that calculates risk for the entire portfolio based
    on market behavior and performance
    """

    def __init__(self) -> None:
        pass


class AssetRiskMenagment:
    """
    Calculates, on the basis of the symbol data and the behavior of the
    entire portfolio, the size of the position and the starting stoplos
    and optimum take profit for the position
    """

    def __init__(self) -> None:
        pass
