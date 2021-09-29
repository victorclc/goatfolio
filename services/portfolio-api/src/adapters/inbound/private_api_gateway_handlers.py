import logging
import traceback
from http import HTTPStatus

from adapters.inbound import investment_core
from adapters.outbound.cedro_stock_intraday_client import (
    cache_snapshot,
    invalidate_cache,
)
from domain.models.investment_request import InvestmentRequest
from goatcommons.utils import JsonUtils

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def batch_add_investments_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        investments = map(
            lambda i: InvestmentRequest(**i), JsonUtils.load(event["body"])
        )
        investment_core.batch_add(investments)
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


def get_cache_snapshot_handler(event, context):
    return {
        "statusCode": HTTPStatus.OK,
        "body": JsonUtils.dump(cache_snapshot()),
    }


def invalidate_cache_handler(event, context):
    invalidate_cache()
    return {
        "statusCode": HTTPStatus.OK,
        "body": JsonUtils.dump(HTTPStatus.OK.phrase),
    }
