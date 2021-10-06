import logging

from core import EventNotifierCore
from goatcommons.utils import JsonUtils
from models import NotifyRequest

logger = logging.getLogger()


def shit_notify_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = EventNotifierCore()

    for message in event['Records']:
        request = NotifyRequest(**JsonUtils.load(message['body']))
        core.notify(request)
