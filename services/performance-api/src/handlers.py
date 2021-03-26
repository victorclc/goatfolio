import logging
import traceback
from decimal import Decimal
from http import HTTPStatus

from goatcommons.models import StockInvestment
from goatcommons.utils import AWSEventUtils, JsonUtils
from core import PerformanceCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = PerformanceCore()


def get_performance_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        result = core.calculate_portfolio_performance(subject)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result.to_dict())}
    except AssertionError as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


def get_today_variation_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        result = core.calculate_today_variation(subject)
        return {'statusCode': HTTPStatus.OK, 'body': JsonUtils.dump(result)}
    except AssertionError as ex:
        logger.error(ex)
        return {'statusCode': HTTPStatus.BAD_REQUEST, 'body': JsonUtils.dump({"message": str(ex)})}


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
        core.consolidate_port_new_and_old_change_name(subject, new_investments, old_investments)
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
    mocked_event = {'Records': [
        {'eventID': '9c12b79e210c4c71fd9323161bacebb1', 'eventName': 'INSERT', 'eventVersion': '1.1',
         'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-2',
         'dynamodb': {'ApproximateCreationDateTime': 1615661773.0,
                      'Keys': {'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                               'id': {'S': 'CEIBBAS3161395200020029011'}},
                      'NewImage': {'date': {'N': '1613952000'}, 'costs': {'N': '0'}, 'amount': {'N': '200'},
                                   'ticker': {'S': 'BBAS3'}, 'price': {'N': '29.01'},
                                   'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                                   'id': {'S': 'CEIBBAS3161395200020029011'},
                                   'broker': {'S': '1099 - INTER DTVM LTDA'},
                                   'type': {'S': 'STOCK'}, 'operation': {'S': 'BUY'},
                                   'external_system': {'S': 'CEI'}},
                      'SequenceNumber': '513247300000000004665050541', 'SizeBytes': 251,
                      'StreamViewType': 'NEW_AND_OLD_IMAGES'},
         'eventSourceARN': 'arn:aws:dynamodb:us-east-2:831967415635:table/Investments/stream/2021-03-13T17:59:42.560'},
        {'eventID': 'edbd2ff5b06bbce9c440bd5068e6604b', 'eventName': 'MODIFY', 'eventVersion': '1.1',
         'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-2',
         'dynamodb': {'ApproximateCreationDateTime': 1615661773.0,
                      'Keys': {'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                               'id': {'S': 'CEIBIDI11161490240022160501'}},
                      'NewImage': {'date': {'N': '1614902400'}, 'costs': {'N': '0'}, 'amount': {'N': '22'},
                                   'ticker': {'S': 'BIDI11'}, 'price': {'N': '160.5'},
                                   'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                                   'id': {'S': 'CEIBIDI11161490240022160501'},
                                   'broker': {'S': '1099 - INTER DTVM LTDA'}, 'type': {'S': 'STOCK'},
                                   'operation': {'S': 'SELL'}, 'external_system': {'S': 'CEI'}},
                      'OldImage': {'date': {'N': '1614902400'}, 'costs': {'N': '1'}, 'amount': {'N': '22'},
                                   'ticker': {'S': 'BIDI11'}, 'price': {'N': '160.5'},
                                   'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                                   'id': {'S': 'CEIBIDI11161490240022160501'},
                                   'broker': {'S': '1099 - INTER DTVM LTDA'}, 'type': {'S': 'STOCK'},
                                   'operation': {'S': 'SELL'}, 'external_system': {'S': 'CEI'}},
                      'SequenceNumber': '513247400000000004665050543', 'SizeBytes': 441,
                      'StreamViewType': 'NEW_AND_OLD_IMAGES'},
         'eventSourceARN': 'arn:aws:dynamodb:us-east-2:831967415635:table/Investments/stream/2021-03-13T17:59:42.560'},
        {'eventID': '9d90858fa3364d4e99a0df39036b42c1', 'eventName': 'INSERT', 'eventVersion': '1.1',
         'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-2',
         'dynamodb': {'ApproximateCreationDateTime': 1615661773.0,
                      'Keys': {'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                               'id': {'S': 'CEIBIDI1116149024007160501'}},
                      'NewImage': {'date': {'N': '1614902400'}, 'costs': {'N': '0'}, 'amount': {'N': '7'},
                                   'ticker': {'S': 'BIDI11'}, 'price': {'N': '160.5'},
                                   'subject': {'S': '440b0d96-395d-48bd-aaf2-58dbf7e68274'},
                                   'id': {'S': 'CEIBIDI1116149024007160501'},
                                   'broker': {'S': '1099 - INTER DTVM LTDA'},
                                   'type': {'S': 'STOCK'}, 'operation': {'S': 'SELL'},
                                   'external_system': {'S': 'CEI'}},
                      'SequenceNumber': '513247500000000004665050544', 'SizeBytes': 254,
                      'StreamViewType': 'NEW_AND_OLD_IMAGES'},
         'eventSourceARN': 'arn:aws:dynamodb:us-east-2:831967415635:table/Investments/stream/2021-03-13T17:59:42.560'}]}
    # # print(core.calculate_portfolio_performance('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    consolidate_portfolio_handler(mocked_event, None)
