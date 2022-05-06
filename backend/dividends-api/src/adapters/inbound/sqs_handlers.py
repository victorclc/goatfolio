from aws_lambda_powertools import Logger, Tracer

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from adapters.outbound.rest_corporate_events_client import RESTCorporateEventsClient
from adapters.outbound.rest_investments_client import RestInvestmentsClient
from adapters.outbound.rest_ticker_info_client import RestTickerInfoClient
from application.models.invesments import StockInvestment
import goatcommons.utils.json as jsonutils
from core.new_investments_consumer import NewInvestmentsConsumer

logger = Logger()
tracer = Tracer()


def parse_subject_new_and_old_investments_from_message(
        message: dict,
) -> (str, StockInvestment, StockInvestment):
    subject = message["attributes"]["MessageGroupId"]
    body = jsonutils.load(message["body"])

    new_json = body.get("new_investment")
    old_json = body.get("old_investment")

    new = StockInvestment(**new_json) if new_json else None
    old = StockInvestment(**old_json) if old_json else None

    return subject, new, old


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def check_for_applicable_dividend_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        subject, new, old = parse_subject_new_and_old_investments_from_message(message)
        corp_client = RESTCorporateEventsClient()
        consumer = NewInvestmentsConsumer(corp_client, corp_client, RestTickerInfoClient(),
                                          DynamoInvestmentRepository(), RestInvestmentsClient())
        consumer.receive(subject, new, old)
