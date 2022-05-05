import datetime
import json
import locale
from typing import List, Protocol

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from adapters.outbound.rest_corporate_events_client import RESTCorporateEventsClient
from adapters.outbound.rest_ticker_info_client import RestTickerInfoClient
from application.models.dividends import CashDividends
from core.helpers import TickerInfoClient, CashDividendsEarningsHelper
from goatcommons.notifications.client import PushNotificationsClient
from goatcommons.notifications.models import NotificationRequest

metrics = Metrics(namespace="DividendsApi", service="NotifyDividends")

logger = Logger()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


class CorporateEventsClient(Protocol):
    def get_cash_dividends(self, date: datetime.date) -> List[CashDividends]:
        ...

    def get_all_previous_symbols(self, isin_code: str) -> List[str]:
        ...


def notify_cash_dividends_job(
        processing_date: datetime.date,
        investments_repository: DynamoInvestmentRepository,
        push_client: PushNotificationsClient,
        corporate_events_client: CorporateEventsClient,
        ticker_info_client: TickerInfoClient
):
    logger.info(f"Notify cash dividends job - START: {processing_date.strftime('%Y-%m-%d')}")

    cash_dividends = corporate_events_client.get_cash_dividends(processing_date)
    helper = CashDividendsEarningsHelper(corporate_events_client, ticker_info_client, investments_repository)

    for dividend in cash_dividends:
        logger.info(f"Processing dividend: {dividend}")
        payouts = helper.calculate_earnings_of_cash_dividend_for_all_users(dividend)

        for payout in payouts:
            subject = payout["subject"]
            ticker = payout["ticker"]
            payed_amount = payout["payed_amount"]

            logger.info(f"Sending push for {subject}.")
            push_client.send(
                NotificationRequest(
                    subject=subject,
                    title="Tem dinheiro entrando! 🐐🎉",
                    message=f"Hoje, você vai receber R$ {locale.currency(payed_amount, grouping=True, symbol=False)} de rendimentos da ação {ticker}"
                )
            )
            metrics.add_metric(name="DividendNotifiedCount", unit=MetricUnit.Count, value=1)

    metrics.add_metric(name="ApplicableCashDividendsCount", unit=MetricUnit.Count, value=len(cash_dividends))
    dump_metrics()
    logger.info(f"Notify cash dividends job - END")


def dump_metrics():
    your_metrics_object = metrics.serialize_metric_set()
    metrics.clear_metrics()
    print(json.dumps(your_metrics_object))


def main():
    repo = DynamoInvestmentRepository()
    notify_cash_dividends_job(datetime.date(2022, 4, 22), repo, PushNotificationsClient(), RESTCorporateEventsClient(),
                              RestTickerInfoClient())


if __name__ == "__main__":
    main()
