from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Key

from goatcommons.notifications.models import NotificationRequest, NotificationMessageRequest
import goatcommons.utils.json as jsonutils


class PushNotificationsClient:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName='PushNotificationRequest')
        self.__table = None

    def init_table(self):
        self.__table = boto3.resource('dynamodb').Table('NotificationMessagesConfig')

    def send_message(self, subject, message_key):
        message = self.fetch_notification_message_config(message_key)
        if message:
            self.send(NotificationRequest(subject, message.title, message.message))

    def send(self, request: NotificationRequest):
        self._queue.send_message(MessageBody=jsonutils.dump(asdict(request)))

    def fetch_notification_message_config(self, message_key):
        if not self.__table:
            self.init_table()
        result = self.__table.query(KeyConditionExpression=Key('message_key').eq(message_key))
        if result['Items']:
            return NotificationMessageRequest(**result['Items'][0])


if __name__ == '__main__':
    PushNotificationsClient().send_message('440b0d96-395d-48bd-aaf2-58dbf7e68274', 'CEI_IMPORT_SUCCESS')
