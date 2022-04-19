from dataclasses import asdict

import boto3

from event_notifier.models import NotifyRequest
import goatcommons.utils.json as jsonutils


class ShitNotifierClient:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName='EventsToNotify')

    def send(self, level, service, message):
        request = NotifyRequest(level, service, message)
        self._queue.send_message(MessageBody=jsonutils.dump(request.to_dict()))
