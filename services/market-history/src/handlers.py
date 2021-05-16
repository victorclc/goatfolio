import logging
import traceback

from core import CotaHistTransformerCore
from goatcommons.shit.client import ShitNotifierClient
from goatcommons.shit.models import NotifyLevel

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def transform_cota_hist_handler(event, context):
    try:
        logger.info(f'EVENT: {event}')
        core = CotaHistTransformerCore()
        for record in event['Records']:
            logger.info(f'Processing record: {record}')
            bucket = record['s3']['bucket']['name']
            file_path = record['s3']['object']['key']
            core.transform_cota_hist(bucket, file_path)
    except Exception:
        traceback.print_exc()
        ShitNotifierClient().send(NotifyLevel.ERROR, 'MARKET-HISTORY',
                                  f'TRANSFORM COTA HIST FAILED {traceback.format_exc()}')


def ibov_history_handler(event, context):
    try:
        logger.info(f'EVENT: {event}')
        core = CotaHistTransformerCore()
        core.update_ibov_history()
    except Exception:
        traceback.print_exc()
        ShitNotifierClient().send(NotifyLevel.ERROR, 'MARKET-HISTORY',
                                  f'IBOV HISTORY FAILED {traceback.format_exc()}')
