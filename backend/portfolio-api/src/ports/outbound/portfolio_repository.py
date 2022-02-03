from typing import Protocol, Optional, List, Type, ClassVar

from domain.common.investment_consolidated import InvestmentConsolidated
from domain.common.portfolio import Portfolio, StockConsolidated, PortfolioItem
from application.models.assets_quantities import AssetQuantities


class PortfolioRepository(Protocol):
    def find(self, subject: str) -> Optional[Portfolio]:
        """Finds the portfolio object of the given subject"""

    def find_ticker(
        self,
        subject: str,
        ticker: str,
        consolidated_type: ClassVar[Type[InvestmentConsolidated]],
    ) -> Optional[List[StockConsolidated]]:
        """Returns all StockConsolidated objects related to the given ticker and subject"""

    def find_all(self, subject) -> (Portfolio, [StockConsolidated]):
        """Returns a tupple containing the portfolio object and the list of all StockConsolidated of given subject"""

    def find_alias_ticker(
        self,
        subject: str,
        ticker: str,
        consolidated_type: ClassVar[Type[InvestmentConsolidated]],
    ) -> Optional[List[StockConsolidated]]:
        """Returns all StockConsolidated objects related to the given alias_ticker and subject"""

    def save_all(self, items: List[PortfolioItem]):
        """Persist a list of PortfolioItems object"""

    def save(self, items: PortfolioItem):
        """Persist a  PortfolioItems object"""

    def find_asset_quantities(self, subject: str) -> Optional[AssetQuantities]:
        """Finds the asset quantities object (if exists)"""
