from typing import List
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key

from domain.common.investments import InvestmentType, Investment, StockInvestment


class MissingRequiredFields(Exception):
    def __init__(self, field, msg):
        self.field = field
        super().__init__(msg)


def load_model_by_type(
    _type: InvestmentType, investment: dict, generate_id: bool = True
) -> Investment:
    investment.pop("type", None)
    if "id" not in investment and not generate_id:
        raise MissingRequiredFields("id", "Missing id field")
    if _type == InvestmentType.STOCK:
        if "id" not in investment:
            investment["id"] = f"STOCK#{investment['ticker'].upper()}#{str(uuid4())}"
        return StockInvestment(**investment, type=InvestmentType.STOCK)
    raise TypeError


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
        )
        return list(
            map(
                lambda i: load_model_by_type(InvestmentType(i["type"]), i),
                result["Items"],
            )
        )

    def save(self, investment: Investment):
        self.__investments_table.put_item(Item=investment.to_json())

    def delete(self, investment_id: str, subject: str):
        self.__investments_table.delete_item(
            Key={"subject": subject, "id": investment_id}
        )

    def batch_save(self, investments: List[Investment]):
        with self.__investments_table.batch_writer() as batch:
            for investment in investments:
                print(investment.to_json())
                batch.put_item(Item=investment.to_json())
