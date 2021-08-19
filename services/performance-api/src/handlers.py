import logging
import traceback
from decimal import Decimal
from http import HTTPStatus

from goatcommons.models import StockInvestment
from goatcommons.shit.client import ShitNotifierClient
from goatcommons.shit.models import NotifyLevel
from goatcommons.utils import AWSEventUtils, JsonUtils
from core import PerformanceCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = PerformanceCore()


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


def consolidate_portfolio_handler(event, context):
    logger.info(f"EVENT: {event}")
    investments_by_subject = {}

    try:
        for record in event['Records']:
            dynamodb = record['dynamodb']
            subject = dynamodb['Keys']['subject']['S']
            if subject not in investments_by_subject:
                investments_by_subject[subject] = {'old_investments': [], 'new_investments': []}
            new_investments = investments_by_subject[subject]['new_investments']
            old_investments = investments_by_subject[subject]['old_investments']
            if 'NewImage' in dynamodb:
                new = _dynamo_stream_to_stock_investment(dynamodb['NewImage'])
                new_investments.append(new)
            if 'OldImage' in dynamodb:
                old = _dynamo_stream_to_stock_investment(dynamodb['OldImage'])
                old_investments.append(old)
        for subject, investment in investments_by_subject.items():
            new_investments = investments_by_subject[subject]['new_investments']
            old_investments = investments_by_subject[subject]['old_investments']
            core.consolidate_portfolio(subject, new_investments, old_investments)
    except Exception:
        traceback.print_exc()
        ShitNotifierClient().send(NotifyLevel.CRITICAL, 'PERFORMANCE-API',
                                  f'CONSOLIDATE PORTFOLIO FAILED {traceback.format_exc()}')


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
                              'alias_ticker': stream['alias_ticker']['S'] if 'NULL' not in stream[
                                  'alias_ticker'] else ''
                              })


if __name__ == '__main__':
    # event = {'pathParameters': {'ticker': 'BIDI11'},
    #          'requestContext': {'authorizer': {'claims': {'sub': '440b0d96-395d-48bd-aaf2-58dbf7e68274'}}}}
    # print(performance_rentability_handler(event, None))
    # print(performance_portfolio_handler(event, None))
    # print(performance_portfolio_ticker_handler(event, None))
    # event = {'Records': [{'eventID': 'f9be0ed70ed3e8cc0f67111a0e783bf7', 'eventName': 'INSERT', 'eventVersion': '1.1',
    #                       'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-2',
    #                       'dynamodb': {'ApproximateCreationDateTime': 1618022461.0,
    #                                    'Keys': {'subject': {'S': '632d0404-53ba-4010-a0c7-b577696f717e'},
    #                                             'id': {'S': '8ffd01f0-3b90-490e-915e-798b05d40575'}},
    #                                    'NewImage': {'date': {'N': '1616716800'}, 'costs': {'N': '0'},
    #                                                 'amount': {'N': '100'}, 'ticker': {'S': 'BIDI11'},
    #                                                 'price': {'N': '150'},
    #                                                 'subject': {'S': '632d0404-53ba-4010-a0c7-b577696f717e'},
    #                                                 'id': {'S': '8ffd01f0-3b90-490e-915e-798b05d40575'},
    #                                                 'broker': {'S': 'Inter'}, 'type': {'S': 'STOCK'},
    #                                                 'operation': {'S': 'BUY'}, 'external_system': {'S': ''}},
    #                                    'SequenceNumber': '643332300000000011560690795', 'SizeBytes': 252,
    #                                    'StreamViewType': 'NEW_AND_OLD_IMAGES'},
    #                       'eventSourceARN': 'arn:aws:dynamodb:us-east-2:831967415635:table/Investments/stream/2021-03-13T17:59:42.560'}]}
    event = {'Records': [{'eventID': 'ad9165823eb6c5a209eb3bd01a949ad1', 'eventName': 'MODIFY', 'eventVersion': '1.1',
                          'eventSource': 'aws:dynamodb', 'awsRegion': 'sa-east-1',
                          'dynamodb': {'ApproximateCreationDateTime': 1629298499.0,
                                       'Keys': {'subject': {'S': '41e4a793-3ef5-4413-82e2-80919bce7c1a'},
                                                'id': {'S': 'CEIVVAR3159528960010020761'}},
                                       'NewImage': {'date': {'N': '1595289600'}, 'alias_ticker': {'S': 'VIIA3'},
                                                    'costs': {'N': '0'}, 'amount': {'N': '100'},
                                                    'ticker': {'S': 'VVAR3'}, 'price': {'N': '20.76'},
                                                    'subject': {'S': '41e4a793-3ef5-4413-82e2-80919bce7c1a'},
                                                    'id': {'S': 'CEIVVAR3159528960010020761'},
                                                    'broker': {'S': '1099 - INTER DTVM LTDA'}, 'type': {'S': 'STOCK'},
                                                    'operation': {'S': 'SELL'}, 'external_system': {'S': ''}},
                                       'OldImage': {'date': {'N': '1595289600'}, 'alias_ticker': {'NULL': True},
                                                    'costs': {'N': '0'}, 'amount': {'N': '100'},
                                                    'ticker': {'S': 'VVAR3'}, 'price': {'N': '20.76'},
                                                    'subject': {'S': '41e4a793-3ef5-4413-82e2-80919bce7c1a'},
                                                    'id': {'S': 'CEIVVAR3159528960010020761'},
                                                    'broker': {'S': '1099 - INTER DTVM LTDA'}, 'type': {'S': 'STOCK'},
                                                    'operation': {'S': 'SELL'}, 'external_system': {'S': ''}},
                                       'SequenceNumber': '98008300000000002716486841', 'SizeBytes': 457,
                                       'StreamViewType': 'NEW_AND_OLD_IMAGES'},
                          'eventSourceARN': 'arn:aws:dynamodb:sa-east-1:138414734174:table/Investments/stream/2021-07-29T00:56:58.028'}]}
    consolidate_portfolio_handler(event, None)
