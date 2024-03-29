from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer

from adapters.out.cognito_user_info_adaptor import CognitoUserInfoAdapter
from adapters.out.dynamo_friend_list_repository import DynamoFriendsRepository
from adapters.out.rest_friends_rentability_adaptor import RESTRentabilityCalculator
from adapters.out.sqs_friend_request_publisher import SQSFriendRequestPublisher
from application.exceptions.invalid_request import InvalidRequest
from application.exceptions.user_not_found import UserNotFound
from application.models.user import User
from core import publish_friend_request, get_friends_list, accept_friend_request, \
    decline_friend_request, cancel_friend_request, remove_friend_request, get_friends_rentability
from goatcommons.utils import aws as awsutilss
from goatcommons.utils import json as jsonutils

logger = Logger()
tracer = Tracer()


def parse_user_from_event(event: dict) -> User:
    claims = event["requestContext"]["authorizer"]["claims"]
    return User(sub=claims["sub"], name=claims["given_name"], email=claims["email"])


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def new_friend_request_handler(event, _):
    from_user = parse_user_from_event(event)
    body = jsonutils.load(event["body"])
    to_email = body["email"].lower()
    user_info = CognitoUserInfoAdapter()
    publisher = SQSFriendRequestPublisher()
    repository = DynamoFriendsRepository()

    try:
        publish_friend_request.publish_friend_request(from_user, to_email, user_info, publisher, repository)
        return {
            "statusCode": HTTPStatus.OK,
            "body": jsonutils.dump(
                {"message": "Convite de compartilhamento enviado."})
        }
    except InvalidRequest as e:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": jsonutils.dump({"message": str(e)})}
    except UserNotFound as e:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": jsonutils.dump({"message": str(e)})}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def accept_friend_request_handler(event, _):
    from_user = parse_user_from_event(event)
    to_user = User(**jsonutils.load(event["body"]))
    publisher = SQSFriendRequestPublisher()
    accept_friend_request.accept_friend_request(from_user, to_user, publisher)
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(
            {"message": "Convite de compartilhamento aceito."})
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def decline_friend_request_handler(event, _):
    from_user = parse_user_from_event(event)
    to_user = User(**jsonutils.load(event["body"]))
    publisher = SQSFriendRequestPublisher()
    decline_friend_request.decline_friend_request(from_user, to_user, publisher)
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(
            {"message": "Convite de compartilhamento recusado."})
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def cancel_friend_request_handler(event, _):
    from_user = parse_user_from_event(event)
    to_user = User(**jsonutils.load(event["body"]))
    publisher = SQSFriendRequestPublisher()
    cancel_friend_request.cancel_friend_request(from_user, to_user, publisher)
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(
            {"message": "Convite de compartilhamento cancelado."})
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_friends_list_handler(event, _):
    result = get_friends_list.get_friends_list(subject=awsutilss.get_event_subject(event),
                                               repository=DynamoFriendsRepository())
    if not result:
        return {"statusCode": HTTPStatus.NOT_FOUND,
                "body": jsonutils.dump({"message": str(HTTPStatus.NOT_FOUND.phrase)})}
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(result.to_dict())
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def remove_friend_handler(event, _):
    from_user = parse_user_from_event(event)
    to_user = User(**jsonutils.load(event["body"]))
    publisher = SQSFriendRequestPublisher()
    remove_friend_request.remove_friend_request(from_user, to_user, publisher)
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(
            {"message": "Amigo removido do seu compartilhamento."})
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_friends_rentability_handler(event, _):
    from_user = parse_user_from_event(event)
    repository = DynamoFriendsRepository()
    calculator = RESTRentabilityCalculator()
    rentability = get_friends_rentability.get_friends_rentability(from_user, repository, calculator)

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([r.to_dict() for r in rentability])
    }
