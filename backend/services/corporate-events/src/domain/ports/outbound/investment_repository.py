import datetime
from typing import Protocol, List

from domain.models.stock_investment import StockInvestment


class InvestmentRepository(Protocol):
    def find_by_subject_and_ticker(self, subject, ticker) -> List[StockInvestment]:
        """Returns all ticker investments of subject"""

    def find_by_ticker_until_date(
        self, ticker, with_date: datetime.date
    ) -> List[StockInvestment]:
        """Returns all ticker investments from all users"""

    def batch_save(self, investments: List[StockInvestment]):
        """Persist a list of StockInvestments"""
