from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional, List

from dateutil.relativedelta import relativedelta

import utils as utils
from domain.performance.stock_subtypes import StockSubtype
from domain.performance.group_position_summary import (
    StockItemInfo,
    StocksPositionSummary,
    REITsPositionSummary,
    BDRsPositionSummary,
    GroupPositionSummary,
)
from domain.performance.intraday_info import IntradayInfo
from domain.common.investment_summary import InvestmentSummary, StockSummary
from domain.performance.performance import (
    PerformanceSummary,
    TickerVariation,
)
from ports.outbound.stock_history_repository import StockHistoryRepository
from ports.outbound.stock_instraday_client import StockIntradayClient


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


class GroupSummaryCalculator(ABC):
    def calculate_group_position_summary(
        self, summaries_dict: Dict[str, InvestmentSummary]
    ) -> List[GroupPositionSummary]:
        """Calculates the position of a group of investments and returns a list of GroupPositionSummary for each
        investment subgroup"""


class StockGroupPositionCalculator(GroupSummaryCalculator):
    def __init__(self, intraday: StockIntradayClient):
        self.intraday = intraday
        self._active_tickers = []
        self._intraday_dict = {}
        self._stocks_summary: Optional[StocksPositionSummary] = None
        self._reits_summary: Optional[REITsPositionSummary] = None
        self._bdrs_summary: Optional[BDRsPositionSummary] = None

    def initialize(self, summaries_dict: Dict[str, StockSummary]):
        active_tickers = [stock for stock, summary in summaries_dict.items()]
        self._intraday_dict: Dict[
            str, IntradayInfo
        ] = self.intraday.batch_get_intraday_info(active_tickers)
        self._stocks_summary = StocksPositionSummary()
        self._reits_summary = REITsPositionSummary()
        self._bdrs_summary = BDRsPositionSummary()

    def create_stock_info(self, ticker: str, summary: StockSummary) -> StockItemInfo:
        return StockItemInfo(
            ticker=ticker,
            quantity=summary.latest_position.amount,
            average_price=summary.latest_position.average_price,
            last_price=self._intraday_dict[ticker].current_price,
            invested_value=summary.latest_position.invested_value,
        )

    @staticmethod
    def create_inactive_stock_info(ticker: str, summary: StockSummary) -> StockItemInfo:
        return StockItemInfo(
            ticker=ticker,
            quantity=summary.latest_position.amount,
            average_price=summary.latest_position.average_price,
            last_price=Decimal(0),
            invested_value=summary.latest_position.invested_value,
        )

    def get_subtype_of_ticker(self, ticker) -> StockSubtype:
        intra: IntradayInfo = self._intraday_dict[ticker]
        if intra.company_name.startswith("FII "):
            return StockSubtype.REIT
        if int(ticker[4:]) > 30:
            return StockSubtype.BDR
        return StockSubtype.STOCK

    def get_non_empty_summaries(self) -> List[StocksPositionSummary]:
        return [
            s
            for s in [self._stocks_summary, self._reits_summary, self._bdrs_summary]
            if not s.is_empty()
        ]

    def calculate_group_position_summary(
        self, summaries_dict: Dict[str, StockSummary]
    ) -> List[StocksPositionSummary]:
        self.initialize(summaries_dict)

        for ticker, summary in summaries_dict.items():
            info = self.create_stock_info(ticker, summary)

            subtype = self.get_subtype_of_ticker(ticker)

            if subtype == StockSubtype.REIT:
                self._reits_summary.add_item_info(info)
            elif subtype == StockSubtype.BDR:
                self._bdrs_summary.add_item_info(info)
            else:
                self._stocks_summary.add_item_info(info)

        return self.get_non_empty_summaries()
