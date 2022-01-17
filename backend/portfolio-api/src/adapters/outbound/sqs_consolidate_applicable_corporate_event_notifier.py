import boto3
from aws_lambda_powertools import Logger

import goatcommons.utils.json as jsonutils
from domain.common.investments import StockInvestment

logger = Logger()


class SQSConsolidateApplicableCorporateEventNotifier:
    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName="ConsolidateApplicableCorporateEvent.fifo")

    def notify(self, subject: str, investment: StockInvestment):
        message = {"subject": subject, "investment": investment.to_json()}
        logger.info(f"Sending message: {message}")
        self._queue.send_message(MessageBody=jsonutils.dump(message), MessageGroupId=subject)
