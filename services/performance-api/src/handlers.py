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


def performance_history_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = core.get_portfolio_history(subject)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}


def portfolio_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    result = core.get_portfolio_list(subject)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}


def ticker_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    subject = AWSEventUtils.get_event_subject(event)
    ticker = AWSEventUtils.get_query_param(event, 'ticker').upper()
    alias_ticker = AWSEventUtils.get_query_param(event, 'alias_ticker').upper()
    result = core.get_ticker_consolidated_history(subject, ticker, alias_ticker)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}
