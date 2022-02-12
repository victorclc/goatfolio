from aws_lambda_powertools import Logger, Tracer
import goatcommons.utils.json as jsonutils
from adapters.out.dynamo_friend_list_repository import DynamoFriendsRepository
from application.models.friend import FriendRequest
from core import friend_request_handler

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def friend_request_listener(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        body = jsonutils.load(message["body"])
        request = FriendRequest(**body)
        repository = DynamoFriendsRepository()
        friend_request_handler.friend_request_handler(request, repository)
