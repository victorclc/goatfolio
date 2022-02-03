import datetime as dt
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from domain.common.investment_consolidated import (
    InvestmentConsolidated,
    StockConsolidated,
)
from domain.common.investment_summary import StockSummary
from domain.common.portfolio_item import PortfolioItem

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

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "initial_date": self.initial_date.strftime(DATE_FORMAT),
            "stocks": {k: v.to_dict() for k, v in self.stocks.items()},
        }

    @property
    def sk(self) -> str:
        return "PORTFOLIO#"

    def update_summary(self, consolidated: InvestmentConsolidated):
        self.initial_date = min(self.initial_date, consolidated.initial_date)
        summary = consolidated.export_investment_summary()

        if isinstance(consolidated, StockConsolidated):
            if not summary:
                if consolidated.current_ticker_name() in self.stocks:  # TODO ENTENDER MELHOR
                    self.stocks.pop(consolidated.current_ticker_name())
                return
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

    def get_stock_summary(self, ticker: str) -> Optional[StockSummary]:
        summary = self.stocks.get(ticker)
        if summary:
            return summary
        for _, item in self.stocks.items():
            if ticker == item.alias_ticker:
                return item
