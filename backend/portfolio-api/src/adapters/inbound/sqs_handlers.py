from datetime import datetime
from itertools import groupby
from typing import List, Optional

from adapters.inbound import portfolio_core, events_consolidated, stock_core, investment_repo, ticker_client
import goatcommons.utils.json as jsonutils
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from adapters.outbound.sqs_consolidate_applicable_corporate_event_notifier import \
    SQSConsolidateApplicableCorporateEventNotifier
from domain.common.investment_loader import load_model_by_type
from domain.common.investments import (
    InvestmentType,
    Investment,
    OperationType,
    StockInvestment,
)
from aws_lambda_powertools import Logger, Tracer

import domain.corporate_events.events_consolidation_strategies as strategy
from domain.corporate_events.earnings_in_assets_event import EarningsInAssetCorporateEvent
from domain.dividends.new_cash_dividend_listener import NewCashDividendListener
from domain.stock_average import save_asset_quantities

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
        if new is not None and new.operation in OperationType.corporate_events_types():
            logger.info(f"Corporate event type, skiping message.")
            continue

        diffs = get_investments_differences(new, old)
        if len(diffs) == 1 and "alias_ticker" in diffs:
            continue

        events_consolidated.check_for_applicable_corporate_events(
            subject,
            [i for i in [new, old] if i is not None],
            strategy.handle_earning_in_assets_event,
        )


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def persist_cei_asset_quantities_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        body = jsonutils.load(message["body"])
        save_asset_quantities.save_asset_quantities(body["subject"], body["asset_quantities"],
                                                    datetime.strptime(body["date"], "%Y%m%d"),
                                                    DynamoPortfolioRepository())


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def new_applicable_corporate_event_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        new_event = EarningsInAssetCorporateEvent(**jsonutils.load(message["body"]))

        logger.info(f"EarningsAssetCorporateEvent: {new_event}")
        ticker = ticker_client.get_ticker_from_isin_code(new_event.isin_code)
        if new_event.subject:
            investments = investment_repo.find_by_subject_and_ticker(new_event.subject, ticker, new_event.with_date)
            logger.info(f"Subject {new_event.subject} has {len(investments)} applicable investments")
        else:
            investments = investment_repo.find_by_ticker_until_date(ticker, new_event.with_date)
            logger.info(f"Total of {len(investments)} applicable investments")

        notifier = SQSConsolidateApplicableCorporateEventNotifier()
        for subject, sub_investments in groupby(sorted(investments, key=lambda i: i.subject), key=lambda i: i.subject):
            notifier.notify(subject, min(list(sub_investments), key=lambda i: i.date))


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def process_applicable_corporate_event_handler(event, context):
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        message = jsonutils.load(message["body"])
        subject = message["subject"]
        investment = StockInvestment(**message["investment"])

        events_consolidated.check_for_applicable_corporate_events(subject, [investment],
                                                                  strategy.handle_earning_in_assets_event)


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def consolidate_dividend_handler(event, context):
    listener = NewCashDividendListener(DynamoPortfolioRepository())
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        subject, new, old = parse_subject_new_and_old_investments_from_message(message)
        listener.receive(subject, new, old)


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
