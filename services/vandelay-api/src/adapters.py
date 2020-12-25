from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Key

from models import Import, CEIOutboundRequest


class ImportsRepository:
    def __init__(self):
        self._table = boto3.resource('dynamodb').Table('Imports')

    def save(self, _import: Import):
        self._table.put_item(Item=asdict(_import))

    def find_latest(self, subject):
        result = self._table.query(KeyConditionExpression=Key('subject').eq(subject), ScanIndexForward=True, Limit=1)
        if 'Items' in result and result['Items']:
            return Import(**result['Items'][0])
        return None
