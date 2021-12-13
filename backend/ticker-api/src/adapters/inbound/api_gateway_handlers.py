from http import HTTPStatus

from adapters.out.dynamo_ticker_info_repository import DynamoTickerInfoRepository
import goatcommons.utils.aws as awsutils
from core.ticker_exists import ticker_exists


def ticker_exists_handler(event, context):
    repo = DynamoTickerInfoRepository()
    ticker = awsutils.get_path_param(event, "ticker").upper()

    if ticker_exists(ticker, repo):
        return {"statusCode": HTTPStatus.OK, "body": "OK"}

    return {"statusCode": HTTPStatus.NOT_FOUND, "body": "Not Found"}
