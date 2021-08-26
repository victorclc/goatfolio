import traceback
from dataclasses import asdict
from http import HTTPStatus

from adapters import InvestmentRepository
from core import InvestmentCore
from goatcommons.utils import AWSEventUtils, JsonUtils
import logging

from model import InvestmentRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = InvestmentCore(repo=InvestmentRepository())


def get_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        query = AWSEventUtils.get_query_params(event)

        investments = core.get(subject, query_params=query)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump([asdict(i) for i in investments])}
    except AssertionError as ex:
        traceback.print_exc()
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}
    except Exception as e:
        traceback.print_exc()
        raise e


def add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        result = core.add(subject, investment)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        traceback.print_exc()
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}
    except Exception as e:
        traceback.print_exc()
        raise e


def edit_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        result = core.edit(subject, investment)
        return {'statusCode': 200, 'body': JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        traceback.print_exc()
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}
    except Exception as e:
        traceback.print_exc()
        raise e


def delete_investment_handler(event, context):
    logger.info(f"Event: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        investment_id = AWSEventUtils.get_path_param(event, 'investmentid')

        core.delete(subject, investment_id)
        return {'statusCode': 200, 'body': JsonUtils.dump({"message": "Success"})}
    except AssertionError as ex:
        traceback.print_exc()
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}
    except Exception as e:
        traceback.print_exc()
        raise e


def batch_add_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investments = map(lambda i: InvestmentRequest(**i), JsonUtils.load(event['body']))
        core.batch_add(investments)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(HTTPStatus.OK.phrase)}
    except Exception as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}
    except Exception as e:
        traceback.print_exc()
        raise e


def async_add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    for message in event['Records']:
        logger.info(f'Processing message: {message}')
        request = InvestmentRequest(**JsonUtils.load(message['body']))
        core.add(request.subject, request)
