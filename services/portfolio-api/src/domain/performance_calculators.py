import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional

from dateutil.relativedelta import relativedelta

import domain.utils as utils
from domain.models.intraday_info import IntradayInfo
from domain.models.investment_consolidated import (
    InvestmentConsolidated,
    StockConsolidated,
)
from domain.models.investment_summary import InvestmentSummary, StockSummary
from domain.models.performance import (
    PerformanceSummary,
    TickerVariation,
    PortfolioPosition,
    CandleData,
)
from domain.ports.outbound.stock_history_repository import StockHistoryRepository
from domain.ports.outbound.stock_instraday_client import StockIntradayClient


class InvestmentPerformanceCalculator(ABC):
    @abstractmethod
    def calculate_performance_summary(
        self, summaries_dict: Dict[str, InvestmentSummary]
    ) -> PerformanceSummary:
        """Calculates the PerformanceSummary of all investments of a investment type"""


class InvestmentHistoricalConsolidator(ABC):
    @abstractmethod
    def consolidate_historical_data_monthly(
        self, consolidations: [InvestmentConsolidated]
    ) -> [PortfolioPosition]:
        """Consolidates the historical data of a investment type"""


class StockPerformanceCalculator(InvestmentPerformanceCalculator):
    def __init__(self, history: StockHistoryRepository, intraday: StockIntradayClient):
        self.history = history
        self.intraday = intraday

    def calculate_performance_summary(
        self, summaries_dict: Dict[str, StockSummary]
    ) -> PerformanceSummary:
        intraday_dict = self.intraday.batch_get_intraday_info(
            list(summaries_dict.keys())
        )

        p = PerformanceSummary()
        previous_month_gross_amount = Decimal(0)
        for ticker, summary in summaries_dict.items():
            intra = intraday_dict.get(ticker)
            p.gross_amount += summary.latest_position.amount * intra.current_price
            p.invested_amount += summary.latest_position.invested_value
            p.day_variation += summary.latest_position.amount * (
                intra.current_price - intra.yesterday_price
            )
            previous_month_gross_amount += self.previous_month_gross_amount(
                ticker, summary
            )
            if utils.is_on_same_year_and_month(
                summary.latest_position.date, utils.current_month_start()
            ):
                p.month_variation -= summary.latest_position.bought_value

            p.ticker_variation.append(
                TickerVariation(
                    ticker, intra.today_variation_percentage, intra.current_price
                )
            )
        p.month_variation += p.gross_amount - previous_month_gross_amount

        return p

    def previous_month_gross_amount(self, ticker, summary: StockSummary) -> Decimal:
        if summary.latest_position.date < utils.current_month_start():
            return (
                summary.latest_position.amount
                * self.history.find_by_ticker_and_date(
                    ticker, utils.current_month_start() - relativedelta(months=1)
                ).close_price
            )
        elif summary.has_active_previous_position():
            return (
                summary.previous_position.amount
                * self.history.find_by_ticker_and_date(
                    ticker, utils.current_month_start() - relativedelta(months=1)
                ).close_price
            )
        return Decimal(0)


class StockHistoricalConsolidator(InvestmentHistoricalConsolidator):
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

        for consolidated in consolidations:
            positions = consolidated.monthly_stock_position_wrapper_linked_list()
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

        return self._history

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
