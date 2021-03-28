import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def transform_cota_hist_handler(event, context):
    logger.info(f'EVENT: {event}')
