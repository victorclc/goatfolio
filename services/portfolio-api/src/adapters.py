from dataclasses import asdict
from typing import List

import boto3
from boto3.dynamodb.conditions import Key

from exceptions import InvestmentNotFoundException
from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils


class InvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource('dynamodb').Table('Investments')

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject))
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))

    def find_by_id_and_subject(self, investment_id, subject) -> Investment:
        result = self.__investments_table.query(
            KeyConditionExpression=Key('subject').eq(subject) & Key('id').eq(investment_id))
        if 'Items' in result and result['Items']:
            investment = result['Items'][0]
            return InvestmentUtils.load_model_by_type(investment['type'], investment)
        raise InvestmentNotFoundException(f'Investment id {investment_id} don\'t exist\'s for subject {subject}')

    def save(self, investment: Investment):
        self.__investments_table.put_item(Item=asdict(investment))

    def delete(self, investment_id, subject):
        self.__investments_table.delete_item(Key={'subject': subject, 'id': investment_id})
