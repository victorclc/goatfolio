from http import HTTPStatus

from core import CEICore
from exceptions import UnprocessableException
from goatcommons.utils import JsonUtils, AWSEventUtils
from models import CEIInboundRequest, CEIImportResult
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = CEICore()


def cei_import_request_handler(event, context):
    logger.info(f'EVENT: {event}')
    try:
        request = CEIInboundRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        core.import_request(subject, request)
        return {'statusCode': HTTPStatus.ACCEPTED.value,
                'body': JsonUtils.dump({"message": HTTPStatus.ACCEPTED.phrase})}
    except TypeError as e:
        return {'statusCode': HTTPStatus.BAD_REQUEST.value, 'body': JsonUtils.dump({"message": str(e)})}
    except UnprocessableException as e:
        return {'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY.value, 'body': JsonUtils.dump({"message": str(e)})}


def cei_import_result_handler(event, context):
    logger.info(f'EVENT: {event}')
    try:
        for message in event['Records']:
            core.import_result(CEIImportResult(**JsonUtils.load(message['body'])))
        return {'statusCode': HTTPStatus.OK.value, 'body': JsonUtils.dump({"message": HTTPStatus.OK.phrase})}
    except Exception as e:
        logger.error(f'CAUGHT EXCEPTION {str(e)}')
        raise


def cei_import_status_handler(event, context):
    pass
