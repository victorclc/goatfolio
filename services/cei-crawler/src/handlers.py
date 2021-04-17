import logging

from core import CEICrawlerCore
from goatcommons.utils import JsonUtils
from models import CEICrawRequest

logger = logging.getLogger()

core = CEICrawlerCore()


def cei_extract_handler(event, context):
    for message in event['Records']:
        request = CEICrawRequest(**JsonUtils.load(message['body']))
        logger.info(f'Starting craw for: {request.subject}')
        core.craw_all_extract(request)
