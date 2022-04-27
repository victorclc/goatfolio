import datetime
import locale
from decimal import Decimal
from itertools import groupby
from typing import List, Protocol

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from adapters.outbound.rest_corporate_events_client import RESTCorporateEventsClient
from adapters.outbound.rest_ticker_info_client import RestTickerInfoClient
from application.models.dividends import CashDividends
from application.models.invesments import StockInvestment, OperationType
from goatcommons.notifications.client import PushNotificationsClient
from goatcommons.notifications.models import NotificationRequest

metrics = Metrics(namespace="CorporateEvents", service="TodayCorporateEvents")

logger = Logger()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


class CorporateEventsClient(Protocol):
    def get_cash_dividends(self, date: datetime.date) -> List[CashDividends]:
        ...

    def get_all_previous_symbols(self, isin_code: str) -> List[str]:
        ...


class TickerInfoClient(Protocol):
    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        ...


def calculate_amount(investments: List[StockInvestment]) -> Decimal:
    amount = Decimal(0)
    for inv in investments:
        if inv.operation in [
            OperationType.BUY,
            OperationType.SPLIT,
            OperationType.INCORP_ADD,
        ]:
            amount = amount + inv.amount
        else:
            amount = amount - inv.amount
    return amount


def notify_cash_dividends_job(
        processing_date: datetime.date,
        investments_repository: DynamoInvestmentRepository,
        push_client: PushNotificationsClient,
        corporate_events_client: CorporateEventsClient,
        ticker_info_client: TickerInfoClient
):
    logger.info(f"Notify cash dividends job - START: {processing_date.strftime('%Y-%m-%d')}")

    cash_dividends = corporate_events_client.get_cash_dividends(processing_date)
    for dividend in cash_dividends:
        logger.info(f"Processing dividend: {dividend}")
        all_isin_symbols = corporate_events_client.get_all_previous_symbols(dividend.asset_issued) \
                           + [dividend.asset_issued]
        tickers = list(
            filter(lambda i: i, map(lambda i: ticker_info_client.get_ticker_from_isin_code(i), all_isin_symbols))
        )
        logger.info(f"Tickers: {tickers}")

        investments = []
        for ticker in tickers:
            investments += investments_repository.find_by_ticker_until_date(ticker, processing_date)
        logger.info(f"Found {len(investments)} applicable investments.")

        for subject, sub_investments in groupby(sorted(investments, key=lambda i: i.subject), key=lambda i: i.subject):
            amount = calculate_amount(list(sub_investments))
            if amount > 0:
                logger.info(f"Sending push for {subject}.")

                push_client.send(
                    NotificationRequest(
                        subject=subject,
                        title="Tem dinheiro entrando! 🐐🎉",
                        message=f"Hoje, você vai receber R$ {locale.currency(dividend.rate * amount, grouping=True, symbol=False)} de rendimentos da ação {tickers[-1]}"
                    )
                )
                metrics.add_metric(name="DividendNotifiedCount", unit=MetricUnit.Count, value=1)
    metrics.add_metric(name="ApplicableCashDividendsCount", unit=MetricUnit.Count, value=len(cash_dividends))
    logger.info(f"Notify cash dividends job - END")


def main():
    repo = DynamoInvestmentRepository()
    notify_cash_dividends_job(datetime.date(2022, 4, 22), repo, PushNotificationsClient(), RESTCorporateEventsClient(),
                              RestTickerInfoClient())


if __name__ == "__main__":
    main()
