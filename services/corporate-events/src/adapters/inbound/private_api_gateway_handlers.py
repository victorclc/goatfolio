import datetime
import logging
from dataclasses import asdict
from http import HTTPStatus

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import corporate_events_core

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_ticker_transformations_handler(event, context):
    logger.info(f"EVENT: {event}")
    ticker = awsutils.get_query_param(event, "ticker")
    date_from = datetime.datetime.strptime(
        awsutils.get_query_param(event, "dateFrom"), "%Y%m%d"
    ).date()
    response = corporate_events_core.transformations_in_ticker(ticker, date_from)

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(asdict(response)),
    }
