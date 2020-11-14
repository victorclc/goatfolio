from dataclasses import asdict

from core import InvestmentCore
from exceptions import InvestmentNotFoundException, BadRequestException
from goatcommons.utils import AwsEventUtils, JsonUtils
import logging

from model import InvestmentRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = InvestmentCore()


def get_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AwsEventUtils.get_event_subject(event)
        investments = core.get_all(subject)

        return {'statusCode': 200, 'body': JsonUtils.dump([asdict(i) for i in investments])}
    except InvestmentNotFoundException as ex:
        return {'statusCode': 404, 'body': JsonUtils.dump({"message": ex})}


def add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AwsEventUtils.get_event_subject(event)
        investment = InvestmentRequest(**JsonUtils.load(event['body']))

        result = core.add(subject, investment)

        return {'statusCode': 200, 'body': JsonUtils.dump(asdict(result))}
    except BadRequestException as ex:
        return {'statusCode': 400, 'body': JsonUtils.dump({"message": ex})}


def edit_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AwsEventUtils.get_event_subject(event)
        investment = InvestmentRequest(**JsonUtils.load(event['body']))

        result = core.edit(subject, investment)

        return {'statusCode': 200, 'body': JsonUtils.dump(asdict(result))}
    except InvestmentNotFoundException as ex:
        return {'statusCode': 404, 'body': JsonUtils.dump({"message": ex})}
    except BadRequestException as ex:
        return {'statusCode': 400, 'body': JsonUtils.dump({"message": ex})}


def delete_investment_handler(event, context):
    logger.info(f"Event: {event}")
    try:
        subject = AwsEventUtils.get_event_subject(event)
        investment_id = AwsEventUtils.get_path_param(event, 'investmentid')

        core.delete(subject, investment_id)
        return {'statusCode': 200, 'body': JsonUtils.dump({"message": "Success"})}
    except InvestmentNotFoundException as ex:
        return {'statusCode': 404, 'body': JsonUtils.dump({"message": ex})}
