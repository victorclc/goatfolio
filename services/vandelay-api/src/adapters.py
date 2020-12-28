from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Key

from goatcommons.utils import JsonUtils
from models import Import, CEIOutboundRequest


class ImportsRepository:
    def __init__(self):
        self._table = boto3.resource('dynamodb').Table('Imports')

    def save(self, _import: Import):
        self._table.put_item(Item=asdict(_import))

    def find(self, subject, datetime):
        result = self._table.query(KeyConditionExpression=Key('subject').eq(subject) & Key('datetime').eq(datetime))
        if 'Items' in result and result['Items']:
            return Import(**result['Items'][0])
        return None

    def find_latest(self, subject):
        result = self._table.query(KeyConditionExpression=Key('subject').eq(subject), ScanIndexForward=True, Limit=1)
        if 'Items' in result and result['Items']:
            return Import(**result['Items'][0])
        return None


class CEIImportsQueue:
    QUEUE_NAME = 'CeiImportRequest'

    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName=self.QUEUE_NAME)

    def send(self, request: CEIOutboundRequest):
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))
