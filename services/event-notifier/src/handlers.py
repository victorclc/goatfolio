import logging

from core import ShitNotifierCore
from goatcommons.utils import JsonUtils
from models import NotifyRequest

logger = logging.getLogger()


def shit_notify_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = ShitNotifierCore()

    for message in event['Records']:
        request = NotifyRequest(**JsonUtils.load(message['body']))
        core.notify(request)
