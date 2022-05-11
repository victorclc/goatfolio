import datetime

from aws_lambda_powertools import Logger, Tracer

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from adapters.outbound.rest_corporate_events_client import RESTCorporateEventsClient
from adapters.outbound.rest_investments_client import RestInvestmentsClient
from adapters.outbound.rest_ticker_info_client import RestTickerInfoClient
from core import notify_cash_dividends_job
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel
from goatcommons.notifications.client import PushNotificationsClient

logger = Logger()
tracer = Tracer()


@notify_exception(Exception, NotifyLevel.ERROR)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def notify_today_cash_dividends_handler(event, context):
    processing_date = datetime.datetime.now().date()
    notify_cash_dividends_job.notify_cash_dividends_job(
        processing_date,
        DynamoInvestmentRepository(),
        PushNotificationsClient(),
        RESTCorporateEventsClient(),
        RestTickerInfoClient(),
        RestInvestmentsClient()
    )
