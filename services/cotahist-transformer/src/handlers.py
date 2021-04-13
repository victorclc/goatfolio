import logging

from core import CotaHistTransformerCore
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def transform_cota_hist_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = CotaHistTransformerCore()
    for record in event['Records']:
        logger.info(f'Processing record: {record}')
        bucket = record['s3']['bucket']['name']
        file_path = record['s3']['object']['key']
        core.transform_cota_hist(bucket, file_path)


def test_request_handler(event, context):
    print(requests.get(
        'https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0=').json())
