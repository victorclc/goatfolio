from dataclasses import asdict
from goatcommons.shit.models import NotifyRequest, NotifyLevel
from goatcommons.utils import JsonUtils

import boto3

boto3.setup_default_session(profile_name='dev')


class ShitNotifierClient:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName='ShitToNotify')

    def send(self, level, service, message):
        request = NotifyRequest(level, service, message);
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))

