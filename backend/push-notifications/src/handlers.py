import logging
from http import HTTPStatus

from core import PushNotificationCore
from goatcommons.notifications.models import NotificationRequest
import goatcommons.utils.json as jsonutils
import goatcommons.utils.aws as aws

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = PushNotificationCore()


def register_token_handler(event, context):
    logger.info(f'EVENT: {event}')
    subject = aws.get_event_subject(event)
    body = jsonutils.load(event['body'])
    token = body['token']
    old_token = body['old_token']

    core.register_token(subject, token, old_token)
    return {'statusCode': HTTPStatus.OK, 'body': jsonutils.dump('Token registered successfully.')}


def unregister_token_handler(event, context):
    logger.info(f'EVENT: {event}')
    subject = aws.get_event_subject(event)
    token = jsonutils.load(event['body'])['token']

    core.unregister_token(subject, token)
    return {'statusCode': HTTPStatus.OK, 'body': jsonutils.dump('Token unregistered successfully.')}


def send_notification_handler(event, context):
    logger.info(f'EVENT: {event}')
    for message in event['Records']:
        request = NotificationRequest(**jsonutils.load(message['body']))
        core.send_notification(request)
