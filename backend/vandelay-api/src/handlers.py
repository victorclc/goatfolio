import datetime
import logging
from dataclasses import asdict
from http import HTTPStatus

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters import (
    ImportsRepository,
    CEIImportsQueue,
    PortfolioClient,
    CEIInfoQueue,
)
from constants import ImportStatus
from core import CEICore
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel
from exceptions import UnprocessableException
from goatcommons.notifications.client import PushNotificationsClient
from models import CEIInboundRequest, CEIImportResult, CEIOutboundRequest

from aws_lambda_powertools import Logger

logger = Logger()

core = CEICore(
    repo=ImportsRepository(),
    queue=CEIImportsQueue(),
    portfolio=PortfolioClient(),
    push=PushNotificationsClient(),
    cei_repo=CEIInfoQueue(),
)


def cei_import_request_handler(event, context):
    try:
        request = CEIInboundRequest(**jsonutils.load(event["body"]))
        subject = awsutils.get_event_subject(event)

        response = core.import_request(subject, request)
        return {
            "statusCode": HTTPStatus.ACCEPTED.value,
            "body": jsonutils.dump(response),
        }
    except TypeError as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": jsonutils.dump({"message": str(e)}),
        }
    except UnprocessableException as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "body": jsonutils.dump({"message": str(e)}),
        }


@notify_exception(Exception, NotifyLevel.ERROR)
def cei_import_result_handler(event, context):
    logger.info(f"EVENT: {event}")

    for message in event["Records"]:
        core.import_result(CEIImportResult(**jsonutils.load(message["body"])))
    return {
        "statusCode": HTTPStatus.OK.value,
        "body": jsonutils.dump({"message": HTTPStatus.OK.phrase}),
    }


@notify_exception(Exception, NotifyLevel.ERROR)
def cei_import_request_error_handler(event, context):
    logger.info(f"EVENT: {event}")

    for message in event["Records"]:
        subject = jsonutils.load(message["body"])["subject"]

        core.import_result(
            CEIImportResult(
                subject,
                int(datetime.datetime.now().timestamp()),
                ImportStatus.ERROR,
                {"error_message": "Message sent do DLQ"},
            )
        )


def import_status_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = awsutils.get_event_subject(event)
        date = awsutils.get_query_param(event, "datetime")
        response = core.import_status(subject, date)
        if not response:
            return {
                "statusCode": HTTPStatus.NOT_FOUND.value,
                "body": jsonutils.dump({"message": HTTPStatus.OK.phrase}),
            }
        return {
            "statusCode": HTTPStatus.OK.value,
            "body": jsonutils.dump(asdict(response)),
        }
    except TypeError as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": jsonutils.dump({"message": str(e)}),
        }
    except UnprocessableException as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "body": jsonutils.dump({"message": str(e)}),
        }
