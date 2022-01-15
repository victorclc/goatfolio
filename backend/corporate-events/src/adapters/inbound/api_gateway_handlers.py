from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.outbound.dynamo_manual_corporate_events_repository import DynamoManualCorporateEventsRepository
from adapters.outbound.rest_ticker_info_client import RESTTickerInfoClient
from application.exceptions.validation_errors import InvalidGroupingFactorError, InvalidLastDatePriorError, \
    InvalidEmittedTickerError
from application.models.manual_event import GroupEvent, SplitEvent, IncorporationEvent
from core import add_manual_corporate_events

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def add_group_corporate_event_handler(event, context):
    repo = DynamoManualCorporateEventsRepository()
    subject = awsutils.get_event_subject(event)
    body = jsonutils.load(event["body"])
    group_event = GroupEvent(**body)

    try:
        add_manual_corporate_events.add_group_corporate_event(subject, group_event, repo)
        return {"statusCode": HTTPStatus.OK,
                "body": jsonutils.dump(
                    {"message": "Evento cadastrado com sucesso. Em instantes sua carteira será consolidada."})}
    except (InvalidGroupingFactorError, InvalidLastDatePriorError) as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": jsonutils.dump({"message": str(e)})}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def add_split_corporate_event_handler(event, context):
    repo = DynamoManualCorporateEventsRepository()
    subject = awsutils.get_event_subject(event)
    body = jsonutils.load(event["body"])
    split_event = SplitEvent(**body)

    try:
        add_manual_corporate_events.add_split_corporate_event(subject, split_event, repo)
        return {"statusCode": HTTPStatus.OK,
                "body": jsonutils.dump(
                    {"message": "Evento cadastrado com sucesso. Em instantes sua carteira será consolidada."})}
    except (InvalidGroupingFactorError, InvalidLastDatePriorError) as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": jsonutils.dump({"message": str(e)})}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def add_incorporation_corporate_event_handler(event, context):
    repo = DynamoManualCorporateEventsRepository()
    ticker_client = RESTTickerInfoClient()
    subject = awsutils.get_event_subject(event)
    body = jsonutils.load(event["body"])
    incorporation_event = IncorporationEvent(**body)

    try:
        add_manual_corporate_events.add_incorporation_corporate_event(subject, incorporation_event, repo, ticker_client)
        return {"statusCode": HTTPStatus.OK,
                "body": jsonutils.dump(
                    {"message": "Evento cadastrado com sucesso. Em instantes sua carteira será consolidada."})}
    except (InvalidEmittedTickerError, InvalidLastDatePriorError) as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": jsonutils.dump({"message": str(e)})}
