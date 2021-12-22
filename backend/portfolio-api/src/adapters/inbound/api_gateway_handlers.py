import datetime
from decimal import Decimal
from http import HTTPStatus

from aws_lambda_powertools import Logger, Tracer

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import performance_core, stock_core, portfolio_core, investment_repo

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

    investment = stock_core.average_price_fix(
        subject,
        body["ticker"],
        datetime.datetime.strptime(body["date_from"], "%Y%m%d").date(),
        body["broker"],
        Decimal(body["amount"]),
        Decimal(body["average_price"]),
    )
    return {"statusCode": 200, "body": jsonutils.dump(investment.to_json())}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def get_stock_divergences_handler(event, context):
    subject = awsutils.get_event_subject(event)

    divergences = stock_core.get_stock_divergences(subject)
    return {"statusCode": 200, "body": jsonutils.dump(divergences)}


def main():
    subject = "206635f0-c196-470e-8201-4eec1d68fc3a"
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

    print(performance_core.calculate_portfolio_summary(subject))
    # print(jsonutils.dump(stock_core.get_stock_divergences(subject)))
    # print(jsonutils.dump(performance_core.ticker_history_chart(subject, "BIDI11").to_json()))


if __name__ == "__main__":
    main()
