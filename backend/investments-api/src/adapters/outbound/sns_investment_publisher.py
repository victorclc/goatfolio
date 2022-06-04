import os
from hashlib import sha256
from typing import Optional

import boto3
from aws_lambda_powertools import Logger

import goatcommons.utils.json as jsonutils
from application.investment import StockInvestment, StockDividend

logger = Logger()


class SNSInvestmentPublisher:
    STOCK_TOPIC_ARN = os.getenv("ADDED_INVESTMENT_TOPIC")
    DIVIDEND_TOPIC_ARN = os.getenv("ADDED_DIVIDEND_TOPIC")

    def __init__(self):
        self.sns = boto3.client("sns")

    def publish_stock_investment(
            self,
            subject: str,
            updated_timestamp: int,
            new_investment: Optional[StockInvestment],
            old_investment: Optional[StockInvestment],
    ):
        self._publish(self.STOCK_TOPIC_ARN, subject, updated_timestamp, new_investment, old_investment)

    def publish_stock_dividend(
            self,
            subject: str,
            updated_timestamp: int,
            new_investment: Optional[StockDividend],
            old_investment: Optional[StockDividend],
    ):
        self._publish(self.DIVIDEND_TOPIC_ARN, subject, updated_timestamp, new_investment, old_investment)

    def _publish(
            self,
            topic: str,
            subject: str,
            updated_timestamp: int,
            new_investment: Optional[StockInvestment],
            old_investment: Optional[StockInvestment],
    ):
        message = {"updated_timestamp": updated_timestamp}
        if new_investment:
            message["new_investment"] = new_investment.to_json()
        if old_investment:
            message["old_investment"] = old_investment.to_json()

        message_json = jsonutils.dump(message)
        response = self.sns.publish(
            TopicArn=topic,
            Message=message_json,
            MessageGroupId=subject,
            MessageDeduplicationId=sha256(message_json.encode('utf8')).hexdigest()
        )
        logger.debug(f"SNS Publish response = {response}")
