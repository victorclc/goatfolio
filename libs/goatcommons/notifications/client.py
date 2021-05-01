from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Key

from goatcommons.notifications.models import NotificationRequest, NotificationMessageRequest
from goatcommons.utils import JsonUtils


class PushNotificationsClient:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName='PushNotificationRequest')
        self.__table = boto3.resource('dynamodb').Table('NotificationMessagesConfig')

    def send(self, request: NotificationRequest):
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))

    def fetch_notification_message_config(self, message_key):
        result = self.__table.query(KeyConditionExpression=Key('message_key').eq(message_key))
        if result['Items']:
            return NotificationMessageRequest(**result['Items'][0])
