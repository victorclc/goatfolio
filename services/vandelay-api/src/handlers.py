from http import HTTPStatus

from core import CEICore
from exceptions import UnprocessableException
from goatcommons.utils import JsonUtils, AWSEventUtils
from models import CEIInboundRequest

core = CEICore()


def cei_import_request_handler(event, context):
    try:
        request = CEIInboundRequest(**JsonUtils.load(event['body']))
        subject = AWSEventUtils.get_event_subject(event)

        core.cei_import_request(subject, request)
        return {'statusCode': HTTPStatus.ACCEPTED.value,
                'body': JsonUtils.dump({"message": HTTPStatus.ACCEPTED.phrase})}
    except TypeError as e:
        return {'statusCode': HTTPStatus.BAD_REQUEST.value, 'body': JsonUtils.dump({"message": str(e)})}
    except UnprocessableException as e:
        return {'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY.value, 'body': JsonUtils.dump({"message": str(e)})}


def cei_import_status_handler(event, context):
    pass
