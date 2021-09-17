import traceback
from dataclasses import asdict
from decimal import Decimal
from http import HTTPStatus

from adapters.out.dynamo_investment_repository import InvestmentRepository
from domain.investment import InvestmentCore
from domain.model.investment_request import InvestmentRequest
from domain.portfolio import PortfolioCore

from goatcommons.models import StockInvestment
from goatcommons.shit.client import ShitNotifierClient
from goatcommons.shit.models import NotifyLevel
from goatcommons.utils import AWSEventUtils, JsonUtils
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = InvestmentCore(repo=InvestmentRepository())


def get_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        query = AWSEventUtils.get_query_params(event)

        investments = core.get(subject, query_params=query)
        return {
            "statusCode": HTTPStatus.OK,
            "body": JsonUtils.dump([asdict(i) for i in investments]),
        }
    except AssertionError as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event["body"]))
        subject = AWSEventUtils.get_event_subject(event)

        result = core.add(subject, investment)
        return {"statusCode": HTTPStatus.OK, "body": JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def edit_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investment = InvestmentRequest(**JsonUtils.load(event["body"]))
        subject = AWSEventUtils.get_event_subject(event)

        result = core.edit(subject, investment)
        return {"statusCode": 200, "body": JsonUtils.dump(asdict(result))}
    except (AssertionError, TypeError) as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def delete_investment_handler(event, context):
    logger.info(f"Event: {event}")
    try:
        subject = AWSEventUtils.get_event_subject(event)
        investment_id = AWSEventUtils.get_path_param(event, "investmentid")

        core.delete(subject, investment_id)
        return {"statusCode": 200, "body": JsonUtils.dump({"message": "Success"})}
    except AssertionError as ex:
        traceback.print_exc()
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def batch_add_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investments = map(
            lambda i: InvestmentRequest(**i), JsonUtils.load(event["body"])
        )
        core.batch_add(investments)
        return {
            "statusCode": HTTPStatus.OK,
            "body": JsonUtils.dump(HTTPStatus.OK.phrase),
        }
    except Exception as ex:
        logger.error(ex)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": JsonUtils.dump({"message": str(ex)}),
        }
    except Exception as e:
        traceback.print_exc()
        raise e


def async_add_investment_handler(event, context):
    logger.info(f"EVENT: {event}")
    for message in event["Records"]:
        logger.info(f"Processing message: {message}")
        request = InvestmentRequest(**JsonUtils.load(message["body"]))
        core.add(request.subject, request)


def consolidate_portfolio_handler(event, context):
    logger.info(f"EVENT: {event}")
    investments_by_subject = {}
    portfolio_core = PortfolioCore(repo=PortfolioRepository())

    try:
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
            portfolio_core.consolidate_portfolio(
                subject, new_investments, old_investments
            )
    except Exception:
        traceback.print_exc()
        ShitNotifierClient().send(
            NotifyLevel.CRITICAL,
            "PERFORMANCE-API",
            f"CONSOLIDATE PORTFOLIO FAILED {traceback.format_exc()}",
        )


def _dynamo_stream_to_stock_investment(stream):
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
            if "NULL" not in stream["alias_ticker"]
            else "",
        }
    )
