import logging

from core import notify
import goatcommons.utils.json as jsonutils
from models import NotifyRequest

logger = logging.getLogger()


def shit_notify_handler(event, context):
    logger.info(f'EVENT: {event}')

    for message in event['Records']:
        request = NotifyRequest(**jsonutils.load(message['body']))
        notify(request)
