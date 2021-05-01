import os
from dataclasses import asdict
from http import HTTPStatus

import boto3
from boto3.dynamodb.conditions import Key

from exceptions import BatchSavingException
from goatcommons.constants import InvestmentsType
from goatcommons.utils import JsonUtils
from models import Import, CEIOutboundRequest, InvestmentRequest
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ImportsRepository:
    def __init__(self):
        self._table = boto3.resource('dynamodb').Table('Imports')

    def save(self, _import: Import):
        data = asdict(_import)
        data.pop('username')
        logger.info(f'Saving import: {data}')
        self._table.put_item(Item=data)

    def find(self, subject, datetime):
        result = self._table.query(KeyConditionExpression=Key('subject').eq(subject) & Key('datetime').eq(datetime))
        if 'Items' in result and result['Items']:
            item = result['Items'][0]
            logger.info(f'Found import request: {item}')
            return Import(**item)
        return None

    def find_latest(self, subject):
        result = self._table.query(KeyConditionExpression=Key('subject').eq(subject), ScanIndexForward=True, Limit=1)
        if 'Items' in result and result['Items']:
            item = result['Items'][0]
            logger.info(f'Found import request: {item}')
            return Import(**item)
        return None


class CEIImportsQueue:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName='CeiImportRequest')

    def send(self, request: CEIOutboundRequest):
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))


class PortfolioClient:
    BATCH_SAVE_ARN = os.getenv('BATCH_SAVE_ARN')

    def __init__(self):
        self.lambda_client = boto3.client('lambda')

    def batch_save(self, investments):
        requests = list(
            map(lambda i: asdict(InvestmentRequest(type=InvestmentsType.STOCK, investment=asdict(i))), investments))
        response = self.lambda_client.invoke(FunctionName=self.BATCH_SAVE_ARN,
                                             Payload=bytes(JsonUtils.dump(requests), encoding='utf8'))

        if response['ResponseMetadata']['HTTPStatusCode'] != HTTPStatus.OK:
            logger.error(f'Batch save failed: {response}')
            raise BatchSavingException()
        return response
