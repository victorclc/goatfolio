import traceback
from datetime import datetime
from http import HTTPStatus
import goatcommons.utils.json as jsonutils
import goatcommons.utils.aws as awsutils
from adapters.inbound import investment_core

from aws_lambda_powertools import Logger, Tracer

from application.exceptions import FieldMissingError, InvalidTicker
from application.investment_loader import MissingRequiredFields
from application.investment_request import InvestmentRequest

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_investments_handler(event, context):
    investments = _get_investments(event, True)

    if isinstance(investments, list):
        return {
            "statusCode": HTTPStatus.OK,
            "body": jsonutils.dump([i.to_json() for i in investments]),
        }
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(investments.to_dict()),
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_investments_v2_handler(event, context):
    investments = _get_investments(event, False)

    if isinstance(investments, list):
        return {
            "statusCode": HTTPStatus.OK,
            "body": jsonutils.dump([i.to_json() for i in investments]),
        }
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(investments.to_dict()),
    }


def _get_investments(event, stock_only):
    subject = awsutils.get_event_subject(event)
    limit = awsutils.get_query_param(event, "limit")
    ticker = awsutils.get_query_param(event, "ticker")
    if limit:
        limit = int(limit)
    last_evaluated_id = awsutils.get_query_param(event, "last_evaluated_id")
    last_evaluated_date = awsutils.get_query_param(event, "last_evaluated_date")
    if last_evaluated_date:
        last_evaluated_date = datetime.strptime(last_evaluated_date, "%Y%m%d").date()

    return investment_core.get(subject, limit, last_evaluated_id, last_evaluated_date, ticker, stock_only)


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def add_investment_handler(event, context):
    try:
        investment = InvestmentRequest(**jsonutils.load(event["body"]))
        subject = awsutils.get_event_subject(event)

        result = investment_core.add(subject, investment)
        return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(result.to_json())}
    except MissingRequiredFields as ex:
        logger.exception("BAD REQUEST", ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": jsonutils.dump({"message": str(ex)}),
        }
    except InvalidTicker as ex:
        logger.exception("BAD REQUEST", ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": jsonutils.dump({"message": str(ex)}),
        }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def edit_investment_handler(event, context):
    try:
        investment = InvestmentRequest(**jsonutils.load(event["body"]))
        subject = awsutils.get_event_subject(event)

        result = investment_core.edit(subject, investment)
        return {"statusCode": 200, "body": jsonutils.dump(result.to_json())}
    except MissingRequiredFields as ex:
        logger.exception("BAD REQUEST", ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": jsonutils.dump({"message": str(ex)}),
        }
    except InvalidTicker as ex:
        logger.exception("BAD REQUEST", ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": jsonutils.dump({"message": str(ex)}),
        }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def delete_investment_handler(event, context):
    try:
        subject = awsutils.get_event_subject(event)
        investment_id = jsonutils.load(event["body"])['investment_id']

        investment_core.delete(subject, investment_id)
        return {"statusCode": 200, "body": jsonutils.dump({"message": "Success"})}
    except FieldMissingError as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": jsonutils.dump({"message": str(ex)}),
        }
