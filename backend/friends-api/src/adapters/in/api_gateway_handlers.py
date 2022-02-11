from adapters.out.cognito_user_info_adaptor import CognitoUserInfoAdapter
from adapters.out.sqs_friend_request_publisher import SQSFriendRequestPublisher
from application.models.user import User
from core import publish_friend_request
from goatcommons.utils import json as jsonutils


def parse_user_from_event(event: dict) -> User:
    claims = event["requestContext"]["authorizer"]["claims"]
    return User(sub=claims["sub"], name=claims["given_name"], email=claims["email"])


def new_friend_request_handler(event, context):
    from_user = parse_user_from_event(event)
    body = jsonutils.load(event["body"])
    to_email = body["email"]
    user_info = CognitoUserInfoAdapter()
    publisher = SQSFriendRequestPublisher()

    publish_friend_request.publish_friend_request(from_user, to_email, user_info, publisher)
