from http import HTTPStatus
from typing import Union

from aws_lambda_powertools import Logger, Tracer

from adapters.out.cognito_user_info_adaptor import CognitoUserInfoAdapter
from adapters.out.sqs_friend_request_publisher import SQSFriendRequestPublisher
from application.exceptions.invalid_request import InvalidRequest
from application.exceptions.user_not_found import UserNotFound
from application.models.user import User
from core import publish_friend_request
from goatcommons.utils import json as jsonutils

logger = Logger()
tracer = Tracer()


def parse_user_from_event(event: dict) -> User:
    claims = event["requestContext"]["authorizer"]["claims"]
    return User(sub=claims["sub"], name=claims["given_name"], email=claims["email"])


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def new_friend_request_handler(event, context):
    from_user = parse_user_from_event(event)
    body = jsonutils.load(event["body"])
    to_email = body["email"]
    user_info = CognitoUserInfoAdapter()
    publisher = SQSFriendRequestPublisher()

    try:
        publish_friend_request.publish_friend_request(from_user, to_email, user_info, publisher)
        return {
            "statusCode": HTTPStatus.OK,
            "body": jsonutils.dump(
                {"message": "Convite de compartilhamento enviado."})
        }
    except InvalidRequest as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": jsonutils.dump({"message": str(e)})}
    except UserNotFound as e:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": jsonutils.dump({"message": str(e)})}
