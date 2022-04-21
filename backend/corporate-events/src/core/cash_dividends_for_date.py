import datetime
import logging
from typing import Protocol, List

from application.entities.cash_dividends import CashDividendsEntity

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CashDividendsRepository(Protocol):
    def find_by_payment_date(self, payment_date: datetime.date) -> List[CashDividendsEntity]:
        ...


def get_cash_dividends(date: datetime.date, cash_dividends_repository: CashDividendsRepository):
    dividends = cash_dividends_repository.find_by_payment_date(date)
    logger.info(f"There is {len(dividends)} dividends for {date.strftime('%Y-%m-%d')}: {dividends}")

    return dividends
