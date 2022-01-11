from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer
import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.outbound.dynamo_manual_corporate_events_repository import DynamoManualCorporateEventsRepository
from application.exceptions.invalid_grouping_factor import InvalidGroupingFactorError
from application.models.manual_event import GroupEvent
from core import add_manual_corporate_events

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def add_grouping_corporate_event_handler(event, context):
    repo = DynamoManualCorporateEventsRepository()
    subject = awsutils.get_event_subject(event)
    body = jsonutils.load(event["body"])
    group_event = GroupEvent(**body)

    try:
        add_manual_corporate_events.add_group_corporate_event(subject, group_event, repo)
        return {"statusCode": HTTPStatus.OK,
                "body": "Evento cadastrado com sucesso. Em instantes sua carteira será consolidada."}
    except InvalidGroupingFactorError as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": str(e)}
