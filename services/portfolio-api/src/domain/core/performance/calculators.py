from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

from dateutil.relativedelta import relativedelta

import domain.utils as utils
from domain.models.investment_summary import InvestmentSummary, StockSummary
from domain.models.performance import (
    PerformanceSummary,
    TickerVariation,
)
from domain.ports.outbound.stock_history_repository import StockHistoryRepository
from domain.ports.outbound.stock_instraday_client import StockIntradayClient


class InvestmentPerformanceCalculator(ABC):
    @abstractmethod
    def calculate_performance_summary(
        self, summaries_dict: Dict[str, InvestmentSummary]
    ) -> PerformanceSummary:
        """Calculates the PerformanceSummary of all investments of a investment type"""


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
