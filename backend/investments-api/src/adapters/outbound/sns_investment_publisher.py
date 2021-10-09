import os
from typing import Optional

import boto3
from aws_lambda_powertools import Logger
import goatcommons.utils.json as json
from domain.investment import Investment

logger = Logger()


class SNSInvestmentPublisher:
    TOPIC_ARN = os.getenv("ADDED_INVESTMENT_TOPIC")

    def __init__(self):
        self.sns = boto3.client("sns")

    def publish(
        self,
        subject: str,
        new_investment: Optional[Investment],
        old_investment: Optional[Investment],
    ):
        response = self.sns.publish(
            TopicArn=self.TOPIC_ARN,
            Message=json.dump(
                {"new_investment": new_investment, "old_investment": old_investment}
            ),
            MessageGroupId=subject,
        )
        logger.debug(f"SNS Publish response = {response}")
