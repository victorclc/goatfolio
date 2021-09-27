import datetime as dt
from dataclasses import dataclass, field
from typing import List, Dict

from domain.models.investment_consolidated import (
    InvestmentConsolidated,
    StockConsolidated,
)
from domain.models.investment_summary import StockSummary
from domain.models.portfolio_item import PortfolioItem

DATE_FORMAT = "%Y%m%d"


@dataclass
class Portfolio(PortfolioItem):
    initial_date: dt.date = dt.datetime.max.date()
    stocks: Dict[str, StockSummary] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.initial_date, str):
            self.initial_date = dt.datetime.strptime(
                self.initial_date, DATE_FORMAT
            ).date()
        new_stocks = {}
        for k, v in self.stocks.items():
            new_stocks[k] = v
            if isinstance(v, dict):
                new_stocks[k] = StockSummary(**v)
        self.stocks = new_stocks

    def to_dict(self) -> dict:
        return {
            **self.__dict__,
            "initial_date": self.initial_date.strftime(DATE_FORMAT),
            "stocks": {k: v.to_dict() for k, v in self.stocks.items()},
        }

    def update_summary(self, consolidated_list: List[InvestmentConsolidated]):
        for consolidated in consolidated_list:
            self.initial_date = min(self.initial_date, consolidated.initial_date)
            summary = consolidated.export_investment_summary()
            if not summary:
                return

            if isinstance(consolidated, StockConsolidated):
                if consolidated.alias_ticker and self.stocks.get(consolidated.ticker):
                    self.stocks.pop(consolidated.ticker)
                self.stocks[consolidated.current_ticker_name()] = summary

    def active_stocks(self) -> Dict[str, StockSummary]:
        return {
            stock: summary
            for stock, summary in self.stocks.items()
            if summary.is_active()
        }

    def active_tickers(self) -> List[str]:
        return [
            ticker for ticker, summary in self.stocks.items() if summary.is_active()
        ]

    def get_stock_summary(self, ticker) -> StockSummary:
        return self.stocks[ticker]
