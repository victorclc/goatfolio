import logging
import traceback
from decimal import Decimal
from http import HTTPStatus

from goatcommons.models import StockInvestment
from goatcommons.utils import AWSEventUtils, JsonUtils
from core import SafePerformanceCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = SafePerformanceCore()


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
    # event = {'pathParameters': {'ticker': 'BIDI11'},
    #          'requestContext': {'authorizer': {'claims': {'sub': '440b0d96-395d-48bd-aaf2-58dbf7e68274'}}}}
    # print(performance_rentability_handler(event, None))
    # print(performance_portfolio_handler(event, None))
    # print(performance_portfolio_ticker_handler(event, None))
    event = {'Records': [{'eventID': 'f9be0ed70ed3e8cc0f67111a0e783bf7', 'eventName': 'INSERT', 'eventVersion': '1.1',
                          'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-2',
                          'dynamodb': {'ApproximateCreationDateTime': 1618022461.0,
                                       'Keys': {'subject': {'S': '632d0404-53ba-4010-a0c7-b577696f717e'},
                                                'id': {'S': '8ffd01f0-3b90-490e-915e-798b05d40575'}},
                                       'NewImage': {'date': {'N': '1616716800'}, 'costs': {'N': '0'},
                                                    'amount': {'N': '100'}, 'ticker': {'S': 'BIDI11'},
                                                    'price': {'N': '150'},
                                                    'subject': {'S': '632d0404-53ba-4010-a0c7-b577696f717e'},
                                                    'id': {'S': '8ffd01f0-3b90-490e-915e-798b05d40575'},
                                                    'broker': {'S': 'Inter'}, 'type': {'S': 'STOCK'},
                                                    'operation': {'S': 'BUY'}, 'external_system': {'S': ''}},
                                       'SequenceNumber': '643332300000000011560690795', 'SizeBytes': 252,
                                       'StreamViewType': 'NEW_AND_OLD_IMAGES'},
                          'eventSourceARN': 'arn:aws:dynamodb:us-east-2:831967415635:table/Investments/stream/2021-03-13T17:59:42.560'}]}
    consolidate_portfolio_handler(event, None)
