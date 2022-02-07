from typing import List

import boto3
from boto3.dynamodb.conditions import Key

from application.models.question import Faq


class DynamoFaqRepository:
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("Faq")

    def find_all(self) -> List[Faq]:
        result = self.__table.scan()
        return list(map(lambda i: Faq(**i), result["Items"]))

    def find(self, topic: str) -> Faq:
        result = self.__table.query(
            KeyConditionExpression=Key("topic").eq(topic)
        )
        return Faq(**result["Items"][0])
