import logging

from core import CEICrawlerCore
from goatcommons.utils import JsonUtils
from models import CEICrawRequest

logger = logging.getLogger()

core = CEICrawlerCore()


def cei_extract_handler(event, context):
    logger.info(f"EVENT: {event}")
    for message in event['Records']:
        logger.info(f'Processing message: {message}')
        core.craw_all_extract(CEICrawRequest(**JsonUtils.load(message['body'])))
