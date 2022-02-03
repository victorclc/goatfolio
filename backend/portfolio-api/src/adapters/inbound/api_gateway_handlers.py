import datetime
from decimal import Decimal
from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import performance_core, stock_core
from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from adapters.outbound.rest_corporate_events_client import RESTCorporateEventsClient
from adapters.outbound.rest_ticker_info_client import RestTickerInfoClient
from domain.stock_average import get_stock_divergences
from domain.stock_average.quick_fix_average_price import average_price_quick_fix

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def performance_summary_handler(event, context):
    subject = awsutils.get_event_subject(event)
    result = performance_core.calculate_portfolio_summary(subject)
    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(result.to_json())}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def performance_history_handler(event, context):
    subject = awsutils.get_event_subject(event)
    result = performance_core.portfolio_history_chart(subject)
    if not result:
        result = []
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump([i.to_json() for i in result]),
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def ticker_performance_handler(event, context):
    subject = awsutils.get_event_subject(event)
    ticker = awsutils.get_path_param(event, "ticker").upper()

    result = performance_core.ticker_history_chart(subject, ticker)
    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(result.to_json())}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def calculate_group_position_summary_handler(event, context):
    subject = awsutils.get_event_subject(event)
    results = performance_core.calculate_portfolio_detailed_summary(subject)

    dict_response = {
        summary.group_name: {
            "opened_positions": summary.opened_positions,
            "gross_value": summary.gross_value,
        }
        for summary in results
    }
    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump(dict_response)}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def fix_average_price_handler(event, context):
    subject = awsutils.get_event_subject(event)
    body = jsonutils.load(event["body"])

    investment = average_price_quick_fix(
        subject,
        body["ticker"],
        datetime.datetime.strptime(body["date_from"], "%Y%m%d").date(),
        body["broker"],
        Decimal(body["amount"]),
        Decimal(body["average_price"]),
        DynamoInvestmentRepository(),
        RESTCorporateEventsClient()
    )
    return {"statusCode": 200, "body": jsonutils.dump(investment.to_json())}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_stock_divergences_handler(event, context):
    subject = awsutils.get_event_subject(event)
    portfolio_repo = DynamoPortfolioRepository()
    client = RESTCorporateEventsClient()
    divergences = get_stock_divergences.get_stock_divergences(subject, portfolio_repo, portfolio_repo, client)
    return {"statusCode": 200, "body": jsonutils.dump(divergences)}


def main():
    subject = "41e4a793-3ef5-4413-82e2-80919bce7c1a"
    # subject = "0ed5d1af-9ae8-402a-898f-6a90633081b8"
    # result = stock_core.average_price_fix(
    #     subject,
    #     **{
    #         "ticker": "MGLU3",
    #
    #         "date": datetime.datetime.strptime("20200503", "%Y%m%d").date(),
    #         "broker": "Inter",
    #         "amount": Decimal(65),
    #         "average_price": Decimal(22.75),
    #     },
    # )
    # print(result)

    # investments = investment_repo.find_by_subject(subject)
    # for investment in investments:
    #     portfolio_core.consolidate_investments(subject, investment, None)

    # print(performance_core.calculate_portfolio_detailed_summary(subject))
    portfolio_repo = DynamoPortfolioRepository()
    client = RESTCorporateEventsClient()
    divergences = get_stock_divergences.get_stock_divergences(subject, portfolio_repo, portfolio_repo, client)
    print(divergences)
    # print(jsonutils.dump(performance_core.ticker_history_chart(subject, "BIDI11").to_json()))


if __name__ == "__main__":
    main()
