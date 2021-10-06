from dataclasses import asdict

import boto3

from goatcommons.utils import JsonUtils
from models import CEICrawResult


class CEIResultQueue:
    QUEUE_NAME = 'CeiImportResult'

    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName=self.QUEUE_NAME)

    def send(self, request: CEICrawResult):
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))
