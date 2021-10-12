import logging
from adapters.inbound import portfolio_core
import goatcommons.utils.json as jsonutils
from domain.common.investment_loader import load_model_by_type
from domain.common.investments import InvestmentType

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def consolidate_investment_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        subject = message["attributes"]["MessageGroupId"]
        body = jsonutils.load(message["body"])

        new_json = body.get("new_investment")
        old_json = body.get("old_investment")

        new = (
            load_model_by_type(InvestmentType(new_json["type"]), new_json, False)
            if new_json
            else None
        )
        old = (
            load_model_by_type(InvestmentType(old_json["type"]), old_json, False)
            if old_json
            else None
        )
        portfolio_core.consolidate_investments(subject, new, old)


if __name__ == '__main__':
    event = {"Records": [{'messageId': 'aa04fc4a-3155-4d02-97cf-61956bf25486', 'receiptHandle': 'AQEBrVJJlEiATYXvQUoIZ5seioZXA96x7uOUi8JnNchDGVZfwjXwuv5Md/5DYak4GkuFpRShTqCh+wxsgWWoR2HNIobq/8fDpIOYs9+zLzgA8rxt7X19WKGMCgZJVRK/SytQ1uYlEJG/jGkIxd8EMoyitpSvcANynWVVyShiQqnQOqtStoYbD0Sz13ge8zThU0DsCi17aprC50iR95ITXFKX4hdP5o2UvALlasUPE9IBr8kzi8GMkWErSO1s8M5tZXNA2YBR/LgEGv0VoDI1ApaiYiQ9ZsiXWaB3mm0srTY+xius36mG7beJEansOklYGyR4', 'body': '{"updated_timestamp": 1634035651, "new_investment": {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "id": "STOCK#BIDI11#56514ecd-9674-4ce7-93c7-9f9981565a26", "date": 20211010, "type": "STOCK", "operation": "BUY", "ticker": "BIDI11", "amount": 10.0, "price": 55.5, "broker": "Inter", "costs": 0.0, "alias_ticker": "", "external_system": ""}}', 'attributes': {'ApproximateReceiveCount': '3', 'SentTimestamp': '1634042139432', 'SequenceNumber': '18865058861404143872', 'MessageGroupId': '41e4a793-3ef5-4413-82e2-80919bce7c1a', 'SenderId': 'AIDAW6YMLC5EDPE7Q5MJL', 'MessageDeduplicationId': '357f1d29a4ec46d5f08fea1995f8a857420bafcef1a0e2a64dec2e2ab846ae98', 'ApproximateFirstReceiveTimestamp': '1634042139432'}, 'messageAttributes': {}, 'md5OfBody': '58d95c7d7932a55eb71f8dfd4fdc7beb', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:sa-east-1:138414734174:PortfolioAddOrUpdatedInvestmentSubscriber.fifo', 'awsRegion': 'sa-east-1'}]}
    consolidate_investment_handler(event, None)