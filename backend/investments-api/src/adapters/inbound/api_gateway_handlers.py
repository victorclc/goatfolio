import traceback
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
    subject = awsutils.get_event_subject(event)
    investments = investment_core.get(subject)

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([i.to_json() for i in investments]),
    }


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
