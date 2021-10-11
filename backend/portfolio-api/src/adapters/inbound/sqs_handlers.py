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
        subject = message["MessageGroupId"]
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
