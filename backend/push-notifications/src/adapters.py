from dataclasses import asdict

import boto3 as boto3
from boto3.dynamodb.conditions import Key

from models import UserTokens


class NotificationTokensRepository:
    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('NotificationTokens')

    def find_user_tokens(self, subject) -> UserTokens:
        result = self.__table.query(KeyConditionExpression=Key('subject').eq(subject))
        if result['Items']:
            return UserTokens(**result['Items'][0])

    def save(self, data: UserTokens):
        self.__table.put_item(Item=asdict(data))
