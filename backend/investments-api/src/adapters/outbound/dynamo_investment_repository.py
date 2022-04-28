from typing import List, Optional, Tuple, Any

import boto3
from boto3.dynamodb.conditions import Key

from application.investment_type import InvestmentType
from application.investment import Investment
import application.investment_loader as il


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_subject(
            self, subject: str,
            limit: Optional[int],
            last_evaluated_id: Optional[str]
    ) -> Tuple[List[Investment], Optional[str]]:
        pagination = {}
        if limit:
            pagination["Limit"] = limit
        if last_evaluated_id:
            pagination["ExclusiveStartKey"] = {"subject": subject, "id": last_evaluated_id}

        result = self.__investments_table.query(
            KeyConditionExpression=Key("subject").eq(subject),
            **pagination
        )
        last_evaluated_key = result.get("LastEvaluatedKey", None)

        return list(
            map(
                lambda i: il.load_model_by_type(InvestmentType(i["type"]), i),
                result["Items"],
            )
        ), last_evaluated_key["id"] if last_evaluated_key else None

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


def main():
    boto3.setup_default_session(profile_name='goatdev')
    subject = "38a883f0-686a-466e-99b3-44a9d0bbd55e"
    repo = DynamoInvestmentRepository()
    last_evaluated_key = 'STOCK#BIDI11#CEI161818560045188011'

    investments = repo.find_by_subject(subject, '20', last_evaluated_key)
    print(investments)
    print(len(investments))


if __name__ == '__main__':
    main()
