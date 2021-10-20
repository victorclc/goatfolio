from adapters.inbound import portfolio_core
import goatcommons.utils.json as jsonutils
from domain.common.investment_loader import load_model_by_type
from domain.common.investments import InvestmentType, Investment, OperationType
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
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

        # validar se unica mudança eh o alias_ticker

        portfolio_core.check_for_applicable_corporate_events(subject, [new, old])
