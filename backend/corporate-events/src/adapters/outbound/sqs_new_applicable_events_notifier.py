import os

import boto3

from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
import goatcommons.utils.json as jsonutils


class SQSNewApplicableEventsNotifier:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName=os.getenv("NEW_APPLICABLE_QUEUE"))

    def notify(self, event: EarningsInAssetCorporateEvent):
        self._queue.send_message(MessageBody=jsonutils.dump(event.to_dict()),
                                 MessageGroupId=event.subject if event.subject else event.id)
