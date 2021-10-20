from http import HTTPStatus

import goatcommons.utils.json as jsonutils
from adapters.outbound.cedro_stock_intraday_client import (
    cache_snapshot,
    invalidate_cache
)

def get_cache_snapshot_handler(event, context):
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(cache_snapshot()),
    }


def invalidate_cache_handler(event, context):
    invalidate_cache()
    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(HTTPStatus.OK.phrase),
    }
