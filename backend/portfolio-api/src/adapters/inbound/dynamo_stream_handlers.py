import logging
from decimal import Decimal

from adapters.inbound import portfolio_core
from domain.models.investment import StockInvestment, Investment
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def consolidate_portfolio_handler(event, context):
    logger.info(f"EVENT: {event}")
    investments_by_subject = {}

    for record in event["Records"]:
        dynamodb = record["dynamodb"]
        subject = dynamodb["Keys"]["subject"]["S"]
        if subject not in investments_by_subject:
            investments_by_subject[subject] = {
                "old_investments": [],
                "new_investments": [],
            }
        new_investments = investments_by_subject[subject]["new_investments"]
        old_investments = investments_by_subject[subject]["old_investments"]
        if "NewImage" in dynamodb:
            new = _dynamo_stream_to_stock_investment(dynamodb["NewImage"])
            new_investments.append(new)
        if "OldImage" in dynamodb:
            old = _dynamo_stream_to_stock_investment(dynamodb["OldImage"])
            old_investments.append(old)
    for subject, investment in investments_by_subject.items():
        new_investments = investments_by_subject[subject]["new_investments"]
        old_investments = investments_by_subject[subject]["old_investments"]
        logger.info(f"New investments = {new_investments}")
        logger.info(f"Old investments = {old_investments}")
        portfolio_core.consolidate_investments(subject, new_investments, old_investments)


def _dynamo_stream_to_stock_investment(stream: dict) -> Investment:
    return StockInvestment(
        **{
            "date": stream["date"]["N"],
            "costs": Decimal(stream["costs"]["N"]),
            "amount": Decimal(stream["amount"]["N"]),
            "ticker": stream["ticker"]["S"],
            "price": Decimal(stream["price"]["N"]),
            "broker": stream["broker"]["S"],
            "type": stream["type"]["S"],
            "operation": stream["operation"]["S"],
            "external_system": stream["external_system"]["S"],
            "subject": stream["subject"]["S"],
            "id": stream["id"]["S"],
            "alias_ticker": stream["alias_ticker"]["S"]
            if "alias_ticker" in stream and "NULL" not in stream["alias_ticker"]
            else "",
        }
    )
