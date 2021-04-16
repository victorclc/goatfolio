import logging
import traceback
from decimal import Decimal

from core import CorporateEventsCore
from goatcommons.models import StockInvestment

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def download_today_corporate_events_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = CorporateEventsCore()
    core.download_today_corporate_events()


def process_corporate_events_file_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = CorporateEventsCore()
    for record in event['Records']:
        logger.info(f'Processing record: {record}')
        bucket = record['s3']['bucket']['name']
        file_path = record['s3']['object']['key']
        core.process_corporate_events_file(bucket, file_path)


def check_for_applicable_corporate_events_handler(event, context):
    logger.info(f"EVENT: {event}")
    new_investments, old_investments = [], []
    subject = None
    core = CorporateEventsCore()
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

        core.check_for_applicable_corporate_events(subject, new_investments + old_investments)
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
