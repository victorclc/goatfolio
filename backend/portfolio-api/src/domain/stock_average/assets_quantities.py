import datetime
from dataclasses import dataclass

from domain.common.portfolio_item import PortfolioItem


@dataclass
class AssetQuantities(PortfolioItem):
    asset_quantities: dict
    date: datetime.date

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.datetime.strptime(self.date, "%Y%m%d")

    @property
    def sk(self) -> str:
        return "STOCKQUANTITIES#"

    def to_json(self):
        return {**super().to_json(), "asset_quantities": self.asset_quantities, "date": self.date.strftime("%Y%m%d")}
