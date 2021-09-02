import logging
from http import HTTPStatus

from adapters import PortfolioRepository, MarketData
from core import PerformanceCore
from goatcommons.utils import AWSEventUtils, JsonUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = PerformanceCore(repo=PortfolioRepository(), market_data=MarketData())


def performance_summary_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = core.get_portfolio_summary(subject)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}


def performance_rentability_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = core.get_portfolio_history(subject)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}


def performance_portfolio_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = core.get_portfolio_list(subject)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}


def performance_portfolio_ticker_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    ticker = AWSEventUtils.get_path_param(event, 'ticker').upper()
    result = core.get_ticker_consolidated_history(subject, ticker)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}
