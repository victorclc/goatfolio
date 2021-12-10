from application.models.user import User


def parse_user_from_event(event: dict) -> User:
    claims = event["requestContext"]["authorizer"]["claims"]
    return User(sub=claims["sub"], name=claims["given_name"], email=claims["email"])


def add_friend_handler(event, context):
    from_user = parse_user_from_event(event)
    
