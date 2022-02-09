from application.models.user import User
from core import add_friend
from goatcommons.utils import json as jsonutils


def parse_user_from_event(event: dict) -> User:
    claims = event["requestContext"]["authorizer"]["claims"]
    return User(sub=claims["sub"], name=claims["given_name"], email=claims["email"])


def add_friend_handler(event, context):
    from_user = parse_user_from_event(event)
    body = jsonutils.load(event["body"])
    to_email = body["email"]
    add_friend.publish_friend_request(from_user, to_email)
