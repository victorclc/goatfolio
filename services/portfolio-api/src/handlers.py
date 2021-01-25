from dataclasses import asdict
from http import HTTPStatus

from core import InvestmentCore
from goatcommons.utils import AWSEventUtils, JsonUtils
import logging

from model import InvestmentRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = InvestmentCore()


def get_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)

        investments = core.get_all(subject)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump([asdict(i) for i in investments])}
    except AssertionError as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


def add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        result = core.add(subject, investment)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


def edit_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        result = core.edit(subject, investment)
        return {'statusCode': 200, 'body': JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


def delete_investment_handler(event, context):
    logger.info(f"Event: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        investment_id = AWSEventUtils.get_path_param(event, 'investmentid')

        core.delete(subject, investment_id)
        return {'statusCode': 200, 'body': JsonUtils.dump({"message": "Success"})}
    except AssertionError as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


def batch_add_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investments = map(lambda i: InvestmentRequest(**i), event)

        core.batch_add(investments)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(HTTPStatus.OK.phrase)}
    except (AssertionError, TypeError) as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}