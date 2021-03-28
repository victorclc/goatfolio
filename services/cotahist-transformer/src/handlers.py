import logging

from core import CotaHistTransformerCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = CotaHistTransformerCore()


def transform_cota_hist_handler(event, context):
    logger.info(f'EVENT: {event}')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        file_path = record['s3']['object']['key']
        core.transform_cota_hist(bucket, file_path)
