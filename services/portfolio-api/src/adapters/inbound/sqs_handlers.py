import logging

from adapters.inbound import investment_core
from domain.models.investment_request import InvestmentRequest
from goatcommons.utils import JsonUtils

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def async_add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        request = InvestmentRequest(**JsonUtils.load(message["body"]))
        investment_core.add(request.subject, request)
