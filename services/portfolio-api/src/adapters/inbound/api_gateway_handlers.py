import logging
import traceback
from dataclasses import asdict
from http import HTTPStatus

from domain.models.investment_request import InvestmentRequest
from domain.utils.investment_loader import MissingRequiredFields
from goatcommons.utils import JsonUtils, AWSEventUtils

from adapters.inbound import investment_core, performance_core

import domain.utils as utils

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_investments_handler(event, context):
    logger.info(f"EVENT: {event}")

    subject = AWSEventUtils.get_event_subject(event)
    investments = investment_core.get(subject)

    return {
        "statusCode": HTTPStatus.OK,
        "body": JsonUtils.dump([asdict(i) for i in investments]),
    }


def add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event["body"]))
        subject = AWSEventUtils.get_event_subject(event)

        result = investment_core.add(subject, investment)
        return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(asdict(result))}
    except MissingRequiredFields as ex:
        logger.exception("BAD REQUEST", ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }


def edit_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event["body"]))
        subject = AWSEventUtils.get_event_subject(event)

        result = investment_core.edit(subject, investment)
        return {"statusCode": 200, "body": JsonUtils.dump(asdict(result))}
    except MissingRequiredFields as ex:
        logger.exception("BAD REQUEST", ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }


def delete_investment_handler(event, context):
    logger.info(f"Event: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        investment_id = AWSEventUtils.get_path_param(event, "investmentid")

        investment_core.delete(subject, investment_id)
        return {"statusCode": 200, "body": JsonUtils.dump({"message": "Success"})}
    except AssertionError as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }


@utils.logexceptions
def performance_summary_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = performance_core.calculate_portfolio_summary(subject)
    return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(result.to_dict())}


def performance_history_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = performance_core.portfolio_history_chart(subject)
    if not result:
        result = []
    return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump([i.to_dict() for i in result])}


def ticker_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    ticker = AWSEventUtils.get_path_param(event, "ticker").upper()

    result = performance_core.ticker_history_chart(subject, ticker)
    return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(result.to_dict())}


def calculate_group_position_summary_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    results = performance_core.calculate_portfolio_detailed_summary(subject)

    dict_response = {
        summary.group_name: {
            "opened_positions": summary.opened_positions,
            "gross_value": summary.gross_value,
        }
        for summary in results
    }
    return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(dict_response)}


def main():
    subject = "41e4a793-3ef5-4413-82e2-80919bce7c1a"
    result = performance_core.portfolio_history_chart(subject)
    print(result)
    # print({"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(result.to_dict())})



if __name__ == "__main__":
    main()
