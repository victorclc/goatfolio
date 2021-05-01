import logging
from http import HTTPStatus

from core import PushNotificationCore
from goatcommons.notifications.models import NotificationRequest
from goatcommons.utils import JsonUtils, AWSEventUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = PushNotificationCore()


def register_token_handler(event, context):
    logger.info(f'EVENT: {event}')
    subject = AWSEventUtils.get_event_subject(event)
    token = JsonUtils.load(event['body'])['token']

    core.register_token(subject, token)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump('Token registered successfully.')}


def unregister_token_handler(event, context):
    logger.info(f'EVENT: {event}')
    subject = AWSEventUtils.get_event_subject(event)
    token = JsonUtils.load(event['body'])['token']

    core.unregister_token(subject, token)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump('Token unregistered successfully.')}


def send_notification_handler(event, context):
    logger.info(f'EVENT: {event}')
    for message in event['Records']:
        request = NotificationRequest(**JsonUtils.load(message['body']))
        core.send_notification(request)
