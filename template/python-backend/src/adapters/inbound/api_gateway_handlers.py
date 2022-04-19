from dataclasses import asdict
from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer

import core.faq as faq
import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.outbound.dynamo_faq_repository import DynamoFaqRepository

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_faq_handler(event, context):
    topic = awsutils.get_query_param(event, "topic").upper()
    data = faq.get_faq(topic, DynamoFaqRepository())

    return {"statusCode": HTTPStatus.OK,
            "body": jsonutils.dump(list(map(lambda f: asdict(f), data)) if type(data) == list else asdict(data))}
