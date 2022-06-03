from typing import List

from application.models.cash_dividends_summary import CashDividendsSummary, CashDividendPosition
from ports.outbound.portfolio_repository import PortfolioRepository


def get_cash_dividends(subject: str, repository: PortfolioRepository) -> List[CashDividendPosition]:
    summary = repository.find_dividends_summary(subject) or CashDividendsSummary(subject)
    return summary.history
