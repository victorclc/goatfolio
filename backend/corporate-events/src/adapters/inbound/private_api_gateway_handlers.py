import datetime
import logging
from dataclasses import asdict
from http import HTTPStatus

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import ticker_client, events_repo
from adapters.outbound.dynamo_manual_corporate_events_repository import DynamoManualCorporateEventsRepository
from core.get_corporate_events import get_corporate_events
from core.ticker_transformations import transformations_in_ticker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_ticker_transformations_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = awsutils.get_query_param(event, "subject")
    ticker = awsutils.get_query_param(event, "ticker")
    date_from = datetime.datetime.strptime(
        awsutils.get_query_param(event, "dateFrom"), "%Y%m%d"
    ).date()
    manual_repo = DynamoManualCorporateEventsRepository()
    response = transformations_in_ticker(ticker, date_from, ticker_client, events_repo, manual_repo, subject)

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(asdict(response)),
    }


def get_corporate_events_handler(event, context):
    subject = awsutils.get_query_param(event, "subject")
    ticker = awsutils.get_query_param(event, "ticker")
    date_from = datetime.datetime.strptime(
        awsutils.get_query_param(event, "dateFrom"), "%Y%m%d"
    ).date()
    manual_repo = DynamoManualCorporateEventsRepository()

    events = get_corporate_events(ticker, date_from, ticker_client, events_repo, manual_repo, subject)

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([e.to_dict() for e in events]),
    }


if __name__ == '__main__':
    subject = None
    ticker = "AESB3"
    date_from = datetime.datetime.strptime(
        "20200731", "%Y%m%d"
    ).date()
    manual_repo = DynamoManualCorporateEventsRepository()
    response = transformations_in_ticker(ticker, date_from, ticker_client, events_repo, manual_repo, subject)
