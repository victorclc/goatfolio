from http import HTTPStatus


from adapters.outbound.dynamo_ticker_info_repository import DynamoTickerInfoRepository
from core.ticker_code_type import ticker_code_type

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters.inbound import ticker_repo
from application.exceptions.IsinNotFound import IsinNotFound
from application.exceptions.TickerNotFound import TickerNotFound
from core.isin_code_from_ticker import isin_code_from_ticker

from core.ticker_exists import ticker_exists
from core.ticker_from_isin_code import ticker_from_isin_code


def ticker_exists_handler(event, context):
    ticker = awsutils.get_path_param(event, "ticker").upper()

    if ticker_exists(ticker, ticker_repo):
        return {"statusCode": HTTPStatus.OK, "body": "OK"}

    return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}



def ticker_code_type_handler(event, context):
    repo = DynamoTickerInfoRepository()
    ticker_code = awsutils.get_path_param(event, "ticker_code").upper()

    response = ticker_code_type(ticker_code, repo)
    if not response:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}

    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump({"asset_type": response})}

def isin_code_from_ticker_handler(event, context):
    ticker = awsutils.get_path_param(event, "ticker").upper()

    try:
        isin = isin_code_from_ticker(ticker, ticker_repo)
        return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump({"isin": isin})}
    except IsinNotFound:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}


def ticker_from_isin_code_handler(event, context):
    isin = awsutils.get_path_param(event, "isin_code").upper()

    try:
        ticker = ticker_from_isin_code(isin, ticker_repo)
        return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump({"ticker": ticker})}
    except TickerNotFound:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}
