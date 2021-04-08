import logging
import traceback
from decimal import Decimal
from http import HTTPStatus

from goatcommons.models import StockInvestment
from goatcommons.utils import AWSEventUtils, JsonUtils
from core import PerformanceCore, SafePerformanceCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = SafePerformanceCore()


def get_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        old_core = PerformanceCore()
        subject = AWSEventUtils.get_event_subject(event)
        result = old_core.calculate_today_performance(subject)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}
    except AssertionError as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


def performance_handler_summary(event, context):
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
    ticker = AWSEventUtils.get_path_param(event, 'ticker')
    result = core.get_ticker_consolidated_history(subject, ticker)
    return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}


def consolidate_portfolio_handler(event, context):
    logger.info(f"EVENT: {event}")
    new_investments, old_investments = [], []
    subject = None
    try:
        for record in event['Records']:
            dynamodb = record['dynamodb']
            if subject is None:
                subject = dynamodb['Keys']['subject']['S']
            if 'NewImage' in dynamodb:
                new = _dynamo_stream_to_stock_investment(dynamodb['NewImage'])
                assert new.subject == subject, 'DIFFERENT SUBJECTS IN THE SAME STREAM'
                new_investments.append(new)
            if 'OldImage' in dynamodb:
                old = _dynamo_stream_to_stock_investment(dynamodb['OldImage'])
                assert old.subject == subject, 'DIFFERENT SUBJECTS IN THE SAME STREAM'
                old_investments.append(old)
        core.consolidate_portfolio(subject, new_investments, old_investments)
    except Exception:
        print(f'CAUGHT EXCEPTION')
        traceback.print_exc()


def _dynamo_stream_to_stock_investment(stream):
    return StockInvestment(**{'date': stream['date']['N'],
                              'costs': Decimal(stream['costs']['N']),
                              'amount': Decimal(stream['amount']['N']),
                              'ticker': stream['ticker']['S'],
                              'price': Decimal(stream['price']['N']),
                              'broker': stream['broker']['S'],
                              'type': stream['type']['S'],
                              'operation': stream['operation']['S'],
                              'external_system': stream['external_system']['S'],
                              'subject': stream['subject']['S'],
                              'id': stream['id']['S'],
                              })


if __name__ == '__main__':
    event = {'pathParameters': {'ticker': 'BIDI11'},
             'requestContext': {'authorizer': {'claims': {'sub': '440b0d96-395d-48bd-aaf2-58dbf7e68274'}}}}
    print(performance_rentability_handler(event, None))
    print(performance_portfolio_handler(event, None))
    print(performance_portfolio_ticker_handler(event, None))
