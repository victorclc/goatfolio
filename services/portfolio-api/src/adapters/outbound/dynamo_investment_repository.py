from typing import List

import boto3
from boto3.dynamodb.conditions import Key

from domain.enums.investment_type import InvestmentType
from domain.models.investment import Investment
import domain.utils.investment_loader as il


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
        )
        return list(
            map(
                lambda i: il.load_model_by_type(InvestmentType.from_string(i["type"]), i),
                result["Items"],
            )
        )

    def save(self, investment: Investment):
        self.__investments_table.put_item(Item=investment.to_dict())

    def delete(self, investment_id: str, subject: str):
        self.__investments_table.delete_item(
            Key={"subject": subject, "id": investment_id}
        )

    def batch_save(self, investments: List[Investment]):
        with self.__investments_table.batch_writer() as batch:
            for investment in investments:
                print(investment.to_dict())
                batch.put_item(Item=investment.to_dict())
