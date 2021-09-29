from abc import ABC, abstractmethod
import datetime
from decimal import Decimal
from typing import Optional, Dict

from domain.models.intraday_info import IntradayInfo
from domain.models.investment_consolidated import (
    InvestmentConsolidated,
    StockConsolidated,
)
from domain.models.performance import PortfolioPosition, CandleData
from domain.ports.outbound.stock_history_repository import StockHistoryRepository
from domain.ports.outbound.stock_instraday_client import StockIntradayClient
import domain.utils as utils


class InvestmentHistoryConsolidator(ABC):
    @abstractmethod
    def consolidate_historical_data_monthly(
        self, consolidations: [InvestmentConsolidated]
    ) -> [PortfolioPosition]:
        """Consolidates the historical data of a investment type"""


class StockHistoryConsolidator(InvestmentHistoryConsolidator):
    def __init__(self, history: StockHistoryRepository, intraday: StockIntradayClient):
        self.ticker_history = history
        self.intraday = intraday
        self._intraday_dict: Optional[Dict[str, IntradayInfo]] = None
        self._history: Dict[datetime.date, PortfolioPosition] = {}

    def initialize(self, tickers):
        self._intraday_dict = self.intraday.batch_get_intraday_info(tickers)
        self._history = {}

    def consolidate_historical_data_monthly(
        self, consolidations: [StockConsolidated]
    ) -> [PortfolioPosition]:
        self.initialize([s.current_ticker_name() for s in consolidations])

        current_month = utils.current_month_start()
        for consolidated in consolidations:
            positions = consolidated.monthly_stock_position_wrapper_linked_list(
                to_date=current_month
            )
            if not positions:
                continue

            historical_data = self.get_historical_data(consolidated)
            for p in positions:
                gross_value = p.amount * self.close_price_of(
                    consolidated, p.date, historical_data
                )
                self.add_to_portfolio_position(
                    p.date, p.node_invested_value, gross_value
                )

        return list(self._history.values())

    def get_historical_data(
        self, consolidated: StockConsolidated
    ) -> Dict[str, Dict[datetime.date, CandleData]]:
        data = {
            consolidated.ticker: self.ticker_history.find_by_ticker_from_date(
                consolidated.ticker, consolidated.initial_date
            )
        }
        if (
            consolidated.alias_ticker
            and consolidated.alias_ticker != consolidated.ticker
        ):
            data[
                consolidated.alias_ticker
            ] = self.ticker_history.find_by_ticker_from_date(
                consolidated.ticker, consolidated.initial_date
            )
        return data

    def close_price_of(
        self,
        consolidated: StockConsolidated,
        date: datetime.date,
        historical_data: Dict[str, Dict[datetime.date, CandleData]],
    ) -> Decimal:
        if date == utils.current_month_start():
            return self._intraday_dict[consolidated.current_ticker_name()].current_price

        if (
            consolidated.alias_ticker in historical_data
            and date in historical_data[consolidated.alias_ticker]
        ):
            return historical_data[consolidated.alias_ticker][date].close_price

        return historical_data[consolidated.ticker][date].close_price

    def get_portfolio_position(self, date: datetime.date) -> PortfolioPosition:
        position = self._history.get(date, PortfolioPosition(date))
        if date not in self._history:
            self._history[date] = position
        return position

    def add_to_portfolio_position(
        self, date: datetime.date, invested_value: Decimal, gross_value: Decimal
    ):
        position = self.get_portfolio_position(date)
        position.invested_value += invested_value
        position.gross_value += gross_value
