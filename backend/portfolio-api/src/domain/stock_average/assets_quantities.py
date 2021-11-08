from dataclasses import dataclass

from domain.common.portfolio_item import PortfolioItem


@dataclass
class AssetQuantities(PortfolioItem):
    asset_quantities: dict

    @property
    def sk(self) -> str:
        return "STOCKQUANTITIES#"

    def to_json(self):
        return {**super().to_json(), "asset_quantities": self.asset_quantities}
