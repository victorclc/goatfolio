from dataclasses import asdict

import boto3

from event_notifier.models import NotifyRequest
from goatcommons.utils import JsonUtils


class ShitNotifierClient:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName='EventsToNotify')

    def send(self, level, service, message):
        request = NotifyRequest(level, service, message)
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))
