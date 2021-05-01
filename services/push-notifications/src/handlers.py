import logging

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


def send_notification_handler(event, context):
    logger.info(f'EVENT: {event}')
    request = NotificationRequest(**JsonUtils.load(event['body']))
    core.send_notification(request)
