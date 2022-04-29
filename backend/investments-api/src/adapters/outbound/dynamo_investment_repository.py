import datetime
from typing import List, Optional, Tuple, Any

import boto3
from boto3.dynamodb.conditions import Key, Attr

from application.investment_type import InvestmentType
from application.investment import Investment
import application.investment_loader as il


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_subject(
            self, subject: str,
            ticker: Optional[str],
            limit: Optional[int],
            last_evaluated_id: Optional[str],
            last_evaluated_date: Optional[datetime.date]
    ) -> Tuple[List[Investment], Optional[str], Optional[datetime.date]]:
        extra_params = {}
        if limit:
            extra_params["Limit"] = limit
        if last_evaluated_id:
            extra_params["ExclusiveStartKey"] = {
                "subject": subject,
                "id": last_evaluated_id,
                "date": int(last_evaluated_date.strftime("%Y%m%d"))
            }
        if ticker:
            extra_params["FilterExpression"] = Attr("ticker").eq(ticker.upper()) | Attr("alias_ticker").eq(
                ticker.upper())

        result = self.__investments_table.query(
            IndexName="subjectDateGlobalIndex",
            ScanIndexForward=False,
            KeyConditionExpression=Key("subject").eq(subject),
            **extra_params
        )
        last_evaluated_key = result.get("LastEvaluatedKey", None)

        return list(
            map(
                lambda i: il.load_model_by_type(InvestmentType(i["type"]), i),
                result["Items"],
            )
        ), last_evaluated_key["id"] if last_evaluated_key else None, datetime.datetime.strptime(str(last_evaluated_key[
                                                                                                        "date"]),
                                                                                                "%Y%m%d").date() if last_evaluated_key else None

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
    last_evaluated_key = 'STOCK#BIDI11#CEI16048800004060061'

    investments = repo.find_by_subject(subject, "BIDI11", None, None, None)
    print(investments)
    print(len(investments))


if __name__ == '__main__':
    main()
