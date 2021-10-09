from aws_lambda_powertools import Logger, Tracer
from boto3.dynamodb.types import TypeDeserializer

from adapters.inbound import investment_core
from domain.investment_loader import load_model_by_type
from domain.investment_type import InvestmentType
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

        investment_core.publish_investment_update(new.subject, new, old)
