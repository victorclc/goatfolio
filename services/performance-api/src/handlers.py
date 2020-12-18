import logging
from http import HTTPStatus

from goatcommons.utils import AwsEventUtils, JsonUtils
from core import PerformanceCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = PerformanceCore()


def get_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AwsEventUtils.get_event_subject(event)
        result = core.calculate_portfolio_performance(subject)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result)}
    except AssertionError as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}
