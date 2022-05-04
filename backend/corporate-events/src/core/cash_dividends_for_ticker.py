import datetime
from typing import Protocol, List

from aws_lambda_powertools import Logger

from application.entities.cash_dividends import CashDividendsEntity
from application.exceptions.not_found_isin import NotFoundIsin
from application.ports.ticker_info_client import TickerInfoClient

logger = Logger()


class CashDividendsRepository(Protocol):
    def find_by_from_last_date_prior(self, isin: str, from_date: datetime.date) -> List[CashDividendsEntity]:
        ...


def get_cash_dividends(
        ticker: str,
        from_date: datetime.date,
        cash_dividends_repository: CashDividendsRepository,
        ticker_client: TickerInfoClient
):
    isin_code = ticker_client.get_isin_code_from_ticker(ticker)
    if not isin_code:
        logger.info(f"Not able to get ISIN_CODE for {ticker}")
        raise NotFoundIsin(f"Not able to get ISIN_CODE for {ticker}")
    dividends = cash_dividends_repository.find_by_from_last_date_prior(isin_code, from_date)
    return dividends
