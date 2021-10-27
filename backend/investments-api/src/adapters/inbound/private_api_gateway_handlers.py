from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer

from adapters.inbound import investment_core
from domain.investment_request import InvestmentRequest
import goatcommons.utils.json as jsonutils

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def batch_add_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investments = map(
            lambda i: InvestmentRequest(**i), jsonutils.load(event["body"])
        )
        investment_core.batch_add(investments)
        return {
            "statusCode": HTTPStatus.OK,
            "body": jsonutils.dump(HTTPStatus.OK.phrase),
        }
    except Exception as ex:
        logger.error(ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": jsonutils.dump({"message": str(ex)}),
        }

