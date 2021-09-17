import logging
import traceback
from dataclasses import asdict
from http import HTTPStatus

from domain.models.investment_request import InvestmentRequest
from goatcommons.utils import JsonUtils, AWSEventUtils

from adapters.inbound import investment_core

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        investments = investment_core.get(subject)

        return {
            "statusCode": HTTPStatus.OK,
            "body": JsonUtils.dump([asdict(i) for i in investments]),
        }
    except AssertionError as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event["body"]))
        subject = AWSEventUtils.get_event_subject(event)

        result = investment_core.add(subject, investment)
        return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def edit_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event["body"]))
        subject = AWSEventUtils.get_event_subject(event)

        result = investment_core.edit(subject, investment)
        return {"statusCode": 200, "body": JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


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
    except Exception as e:
        traceback.print_exc()
        raise e
