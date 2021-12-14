from http import HTTPStatus

from adapters.outbound.dynamo_ticker_info_repository import DynamoTickerInfoRepository
import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from core.ticker_code_type import ticker_code_type
from core.ticker_exists import ticker_exists


def ticker_exists_handler(event, context):
    repo = DynamoTickerInfoRepository()
    ticker = awsutils.get_path_param(event, "ticker").upper()

    if ticker_exists(ticker, repo):
        return {"statusCode": HTTPStatus.OK, "body": "OK"}

    return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}


def ticker_code_type_handler(event, context):
    repo = DynamoTickerInfoRepository()
    ticker_code = awsutils.get_path_param(event, "ticker_code").upper()

    response = ticker_code_type(ticker_code, repo)
    if not response:
        return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}

    return {"statusCode": HTTPStatus.OK, "body": jsonutils.dump({"asset_type": response})}
