from typing import List, Optional

from adapters.inbound import portfolio_core, events_consolidated
import goatcommons.utils.json as jsonutils
from domain.common.investment_loader import load_model_by_type
from domain.common.investments import (
    InvestmentType,
    Investment,
    OperationType,
    StockInvestment,
)
from aws_lambda_powertools import Logger, Tracer

import domain.portfolio.events_consolidation_strategies as strategy

logger = Logger()
tracer = Tracer()


def parse_subject_new_and_old_investments_from_message(
    message: dict,
) -> (str, Investment, Investment):
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
    return subject, new, old


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def consolidate_investment_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        subject, new, old = parse_subject_new_and_old_investments_from_message(message)
        portfolio_core.consolidate_investments(subject, new, old)


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def check_for_applicable_corporate_events_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        subject, new, old = parse_subject_new_and_old_investments_from_message(message)

        if new and new.type in OperationType.corporate_events_types():
            logger.info(f"Corporate event type, skiping message.")
            continue

        diffs = get_investments_differences(new, old)
        if len(diffs) == 1 and "alias_ticker" in diffs:
            continue

        events_consolidated.check_for_applicable_corporate_events(
            subject, [new, old], strategy.handle_earning_in_assets_event
        )


def get_investments_differences(
    inv_1: Optional[StockInvestment], inv_2: Optional[StockInvestment]
) -> List[str]:
    diffs = []
    if not inv_1 or not inv_2:
        return diffs

    if inv_1.type != inv_2.type:
        diffs.append("type")
    if inv_1.date != inv_2.date:
        diffs.append("date")
    if inv_1.ticker != inv_2.ticker:
        diffs.append("ticker")
    if inv_1.alias_ticker != inv_2.alias_ticker:
        diffs.append("alias_ticker")
    if inv_1.amount != inv_2.amount:
        diffs.append("amount")
    if inv_1.price != inv_2.price:
        diffs.append("price")
    if inv_1.operation != inv_2.operation:
        diffs.append("operation")
    if inv_1.price != inv_2.price:
        diffs.append("price")
    return diffs
