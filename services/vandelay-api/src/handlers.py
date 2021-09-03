import traceback
from dataclasses import asdict
from http import HTTPStatus

from adapters import ImportsRepository, CEIImportsQueue, PortfolioClient, CEIInfoRepository
from core import CEICore
from exceptions import UnprocessableException
from goatcommons.notifications.client import PushNotificationsClient
from goatcommons.shit.client import ShitNotifierClient
from goatcommons.shit.models import NotifyLevel
from goatcommons.utils import JsonUtils, AWSEventUtils
from models import CEIInboundRequest, CEIImportResult
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = CEICore(repo=ImportsRepository(), queue=CEIImportsQueue(), portfolio=PortfolioClient(),
               push=PushNotificationsClient(), cei_repo=CEIInfoRepository())


def cei_import_request_handler(event, context):
    try:
        request = CEIInboundRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        response = core.import_request(subject, request)
        return {'statusCode': HTTPStatus.ACCEPTED.value,
                'body': JsonUtils.dump(response)}
    except TypeError as e:
        logger.exception(e)
        return {'statusCode': HTTPStatus.BAD_REQUEST.value, 'body': JsonUtils.dump({"message": str(e)})}
    except UnprocessableException as e:
        logger.exception(e)
        return {'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY.value, 'body': JsonUtils.dump({"message": str(e)})}


def cei_import_result_handler(event, context):
    logger.info(f'EVENT: {event}')
    try:
        for message in event['Records']:
            core.import_result(CEIImportResult(**JsonUtils.load(message['body'])))
        return {'statusCode': HTTPStatus.OK.value, 'body': JsonUtils.dump({"message": HTTPStatus.OK.phrase})}
    except Exception as e:
        logger.exception(e)
        ShitNotifierClient().send(NotifyLevel.ERROR, 'VANDELAY-API',
                                  f'CEI IMPORT RESULT FAILED {traceback.format_exc()}')

        raise


def cei_info_request_handler(event, context):
    logger.info(f'EVENT: {event}')
    try:
        subject = AWSEventUtils.get_event_subject(event)
        response = core.cei_info_request(subject)
        return {'statusCode': HTTPStatus.OK.value, 'body': JsonUtils.dump(response) if response else []}
    except TypeError as e:
        logger.exception(e)
        return {'statusCode': HTTPStatus.BAD_REQUEST.value, 'body': JsonUtils.dump({"message": str(e)})}
    except UnprocessableException as e:
        logger.exception(e)
        return {'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY.value, 'body': JsonUtils.dump({"message": str(e)})}


def import_status_handler(event, context):
    logger.info(f'EVENT: {event}')
    try:
        subject = AWSEventUtils.get_event_subject(event)
        datetime = AWSEventUtils.get_query_params(event)['datetime']
        response = core.import_status(subject, datetime)
        return {'statusCode': HTTPStatus.OK.value, 'body': JsonUtils.dump(asdict(response) if response else {})}
    except TypeError as e:
        logger.exception(e)
        return {'statusCode': HTTPStatus.BAD_REQUEST.value, 'body': JsonUtils.dump({"message": str(e)})}
    except UnprocessableException as e:
        logger.exception(e)
        return {'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY.value, 'body': JsonUtils.dump({"message": str(e)})}
