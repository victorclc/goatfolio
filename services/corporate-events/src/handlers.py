import logging
import traceback
from decimal import Decimal

from core import CorporateEventsCore, CorporateEventsCrawlerCore
from goatcommons.models import StockInvestment

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def download_today_corporate_events_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = CorporateEventsCrawlerCore()
    core.download_today_corporate_events()


def process_corporate_events_file_handler(event, context):
    logger.info(f'EVENT: {event}')
    core = CorporateEventsCrawlerCore()
    for record in event['Records']:
        logger.info(f'Processing record: {record}')
        bucket = record['s3']['bucket']['name']
        file_path = record['s3']['object']['key']
        core.process_corporate_events_file(bucket, file_path)


def check_for_applicable_corporate_events_handler(event, context):
    logger.info(f"EVENT: {event}")
    investments_by_subject = {}
    core = CorporateEventsCore()
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
