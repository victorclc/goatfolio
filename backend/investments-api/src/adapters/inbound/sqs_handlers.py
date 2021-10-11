from aws_lambda_powertools import Logger, Tracer

import goatcommons.utils.json as jsonutils
from adapters.inbound import investment_core
from domain.investment_request import InvestmentRequest

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def async_add_investment_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        request = InvestmentRequest(**jsonutils.load(message["body"]))
        investment_core.add(request.subject, request)
