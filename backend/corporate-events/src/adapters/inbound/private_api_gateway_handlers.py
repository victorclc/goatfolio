import datetime
import logging
from http import HTTPStatus

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import ticker_client, events_repo
from adapters.outbound.dynamo_cash_dividends_repository import DynamoCashDividendsRepository
from adapters.outbound.dynamo_corporate_events_repository import DynamoCorporateEventsRepository
from adapters.outbound.dynamo_manual_corporate_events_repository import DynamoManualCorporateEventsRepository
from adapters.outbound.rest_ticker_info_client import RESTTickerInfoClient
from core import cash_dividends_for_date, get_all_previous_symbols, cash_dividends_for_ticker
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
        "body": jsonutils.dump(response.to_dict()),
    }


def get_corporate_events_handler(event, context):
    subject = awsutils.get_query_param(event, "subject")
    ticker = awsutils.get_query_param(event, "ticker")
    isin_code = awsutils.get_query_param(event, "isin_code")
    date_from = datetime.datetime.strptime(
        awsutils.get_query_param(event, "dateFrom"), "%Y%m%d"
    ).date()
    manual_repo = DynamoManualCorporateEventsRepository()

    if not ticker and not isin_code:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": "Ticker and isin_code can be both null"}

    events = get_corporate_events(ticker, isin_code, date_from, ticker_client, events_repo, manual_repo, subject)

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([e.to_dict() for e in events]),
    }


def get_cash_dividends_handler(event, context):
    date = datetime.datetime.strptime(
        awsutils.get_query_param(event, "date"), "%Y%m%d"
    ).date()

    dividends = cash_dividends_for_date.get_cash_dividends(date, DynamoCashDividendsRepository())

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([d.to_dict() for d in dividends]),
    }


def get_all_previous_symbols_handler(event, context):
    isin_code = awsutils.get_query_param(event, "isin_code")
    symbols = get_all_previous_symbols.get_all_previous_symbols(isin_code, DynamoCorporateEventsRepository())

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(symbols),
    }


def get_ticker_cash_dividends_handler(event, context):
    from_date = datetime.datetime.strptime(
        awsutils.get_query_param(event, "from_date"), "%Y%m%d"
    ).date()
    ticker = awsutils.get_path_param(event, "ticker").upper()

    dividends = cash_dividends_for_ticker.get_cash_dividends(
        ticker,
        from_date,
        DynamoCashDividendsRepository(),
        RESTTickerInfoClient()
    )
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([d.to_dict() for d in dividends]),
    }


def main():
    subject = None
    ticker = "AESB3"
    date_from = datetime.datetime.strptime(
        "20200731", "%Y%m%d"
    ).date()
    manual_repo = DynamoManualCorporateEventsRepository()
    response = transformations_in_ticker(ticker, date_from, ticker_client, events_repo, manual_repo, subject)
