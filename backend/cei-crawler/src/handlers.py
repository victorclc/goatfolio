import logging

from core import CEICrawlerCore
import goatcommons.utils.json as jsonutils
from models import CEICrawRequest

logger = logging.getLogger()


def cei_extract_handler(event, context):
    core = CEICrawlerCore()
    for message in event['Records']:
        request = CEICrawRequest(**jsonutils.load(message['body']))
        logger.info(f'Starting craw for: {request.subject}')
        core.craw_all_extract(request)
