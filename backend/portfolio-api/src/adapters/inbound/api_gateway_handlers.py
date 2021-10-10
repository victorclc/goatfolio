import datetime
import logging
from decimal import Decimal
from http import HTTPStatus

import utils as utils
import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import performance_core, stock_core

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@utils.logexceptions
def performance_summary_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = awsutils.get_event_subject(event)
    result = performance_core.calculate_portfolio_summary(subject)
    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(result.to_dict())}


def performance_history_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = awsutils.get_event_subject(event)
    result = performance_core.portfolio_history_chart(subject)
    if not result:
        result = []
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([i.to_dict() for i in result]),
    }


def ticker_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = awsutils.get_event_subject(event)
    ticker = awsutils.get_path_param(event, "ticker").upper()

    result = performance_core.ticker_history_chart(subject, ticker)
    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(result.to_dict())}


def calculate_group_position_summary_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = awsutils.get_event_subject(event)
    results = performance_core.calculate_portfolio_detailed_summary(subject)

    dict_response = {
        summary.group_name: {
            "opened_positions": summary.opened_positions,
            "gross_value": summary.gross_value,
        }
        for summary in results
    }
    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(dict_response)}


def fix_average_price_handler(event, context):
    logger.info(f"EVENT: {event}")

    subject = awsutils.get_event_subject(event)
    body = jsonutils.load(event["body"])

    investment = stock_core.average_price_fix(
        subject,
        body["ticker"],
        datetime.datetime.strptime(body["date_from"], "%Y%m%d").date(),
        body["broker"],
        Decimal(body["amount"]),
        Decimal(body["average_price"]),
    )
    return {"statusCode": 200, "body": jsonutils.dump(investment.to_dict())}


def main():
    subject = "41e4a793-3ef5-4413-82e2-80919bce7c1a"
    result = stock_core.average_price_fix(
        subject,
        **{
            "ticker": "AESB3",
            "date_from": datetime.datetime.strptime("20210101", "%Y%m%d").date(),
            "broker": "Inter",
            "amount": 10,
            "average_price": 15,
        },
    )
    print(result)
    # print({"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(result.to_dict())})


if __name__ == "__main__":
    main()
