from aws_lambda_powertools import Logger, Tracer
from boto3.dynamodb.types import TypeDeserializer

from adapters.inbound import investment_core
from application.investment_loader import load_model_by_type
from application.investment_type import InvestmentType
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel

logger = Logger()
tracer = Tracer()


@notify_exception(Exception, NotifyLevel.CRITICAL)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def publish_investment_update_handler(event, context):
    deserializer = TypeDeserializer()
    for record in event["Records"]:
        dynamo_record = record["dynamodb"]
        new = None
        old = None

        if "NewImage" in dynamo_record:
            i = deserializer.deserialize({"M": dynamo_record["NewImage"]})
            new = load_model_by_type(InvestmentType(i["type"]), i, generate_id=False)
        if "OldImage" in dynamo_record:
            i = deserializer.deserialize({"M": dynamo_record["OldImage"]})
            old = load_model_by_type(InvestmentType(i["type"]), i, generate_id=False)

        investment_core.publish_investment_update(
            dynamo_record["Keys"]["subject"]["S"],
            int(dynamo_record["ApproximateCreationDateTime"]),
            new,
            old,
        )


if __name__ == "__main__":
    event = {
        "Records": [
            {
                "eventID": "50a29e78fff07932e5b587636635dd49",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "sa-east-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1634035651,
                    "Keys": {
                        "subject": {"S": "41e4a793-3ef5-4413-82e2-80919bce7c1a"},
                        "id": {
                            "S": "STOCK#BIDI11#56514ecd-9674-4ce7-93c7-9f9981565a26"
                        },
                    },
                    "NewImage": {
                        "date": {"N": "20211010"},
                        "alias_ticker": {"S": ""},
                        "costs": {"N": "0"},
                        "amount": {"N": "10"},
                        "ticker": {"S": "BIDI11"},
                        "price": {"N": "55.5"},
                        "subject": {"S": "41e4a793-3ef5-4413-82e2-80919bce7c1a"},
                        "id": {
                            "S": "STOCK#BIDI11#56514ecd-9674-4ce7-93c7-9f9981565a26"
                        },
                        "broker": {"S": "Inter"},
                        "type": {"S": "STOCK"},
                        "operation": {"S": "BUY"},
                        "external_system": {"S": ""},
                    },
                    "SequenceNumber": "100000000003731584075",
                    "SizeBytes": 290,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:sa-east-1:138414734174:table/Investments/stream/2021-10-12T08:50:50.180",
            }
        ]
    }

    publish_investment_update_handler(event, None)
