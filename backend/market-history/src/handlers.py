import logging
import traceback

from core import CotaHistTransformerCore, CotaHistDownloaderCore
from goatcommons.shit.client import ShitNotifierClient
from goatcommons.shit.models import NotifyLevel
from goatcommons.utils import JsonUtils

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


def download_current_monthly_cotahist_file(event, context):
    logger.info(f'EVENT: {event}')
    try:
        core = CotaHistDownloaderCore()
        core.download_current_monthly_file()
    except Exception as e:
        logger.exception('Exception on dowload urrent monthly cotahist file', e)
        ShitNotifierClient().send(NotifyLevel.CRITICAL, 'MARKET-HISTORY',
                                  f'MONTHLY COTAHIST FAILED {traceback.format_exc()}')


def download_monthly_cotahist_file(event, context):
    logger.info(f'EVENT: {event}')
    body = JsonUtils.load(event['body'])
    core = CotaHistDownloaderCore()
    core.download_monthly_file(body['year'], body['month'])
