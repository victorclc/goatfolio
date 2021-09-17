from typing import Protocol, Optional, List

from domain.models.portfolio import Portfolio, StockConsolidated


class PortfolioRepository(Protocol):
    def find(self, subject: str) -> Portfolio:
        """Finds the portfolio object of the given subject"""

    def find_ticker(
        self, subject: str, ticker: str
    ) -> Optional[List[StockConsolidated]]:
        """Returns all StockConsolidated objects related to the given ticker and subject"""

    def find_alias_ticker(
        self, subject: str, ticker: str
    ) -> Optional[List[StockConsolidated]]:
        """Returns all StockConsolidated objects related to the given alias_ticker and subject"""

    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Persist portfolio object in database"""

    def save_stock_consolidated(self, stock_consolidated: StockConsolidated) -> None:
        """Persist StockConsolidated object in database"""
