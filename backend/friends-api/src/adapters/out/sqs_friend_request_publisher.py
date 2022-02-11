import boto3
from aws_lambda_powertools import Logger
import goatcommons.utils.json as jsonutils

from application.models.friend import FriendRequest, RequestType

logger = Logger()


class SQSFriendRequestPublisher:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName="FriendRequest.fifo")

    def notify(self, request: FriendRequest):
        message = jsonutils.dump(request.to_dict())
        if request.type_ == RequestType.TO:
            logger.info(f"Sending 'to' message: {message}")
            self._queue.send_message(MessageBody=message, MessageGroupId=request.to.sub)
        else:
            logger.info(f"Sending 'from' message: {message}")
            self._queue.send_message(MessageBody=message, MessageGroupId=request.from_.sub)
