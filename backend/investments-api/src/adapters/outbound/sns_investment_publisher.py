import os
from hashlib import sha256
from typing import Optional

import boto3
from aws_lambda_powertools import Logger
import goatcommons.utils.json as jsonutils
from application.investment import Investment

logger = Logger()


class SNSInvestmentPublisher:
    TOPIC_ARN = os.getenv("ADDED_INVESTMENT_TOPIC")

    def __init__(self):
        self.sns = boto3.client("sns")

    def publish(
        self,
        subject: str,
        updated_timestamp: int,
        new_investment: Optional[Investment],
        old_investment: Optional[Investment],
    ):
        message = {"updated_timestamp": updated_timestamp}
        if new_investment:
            message["new_investment"] = new_investment.to_json()
        if old_investment:
            message["old_investment"] = old_investment.to_json()

        message_json = jsonutils.dump(message)
        response = self.sns.publish(
            TopicArn=self.TOPIC_ARN,
            Message=message_json,
            MessageGroupId=subject,
            MessageDeduplicationId=sha256(message_json.encode('utf8')).hexdigest()
        )
        logger.debug(f"SNS Publish response = {response}")
