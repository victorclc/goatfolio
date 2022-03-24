from http import HTTPStatus

import goatcommons.utils.json as jsonutils
from adapters.inbound import performance_core
from adapters.outbound.cedro_stock_intraday_client import (
    cache_snapshot,
    invalidate_cache
)
from domain.performance.get_portfolio_summary_for_subjects import get_performance_summary_for_subjects


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


def get_performance_summary_for_subjects_handler(event, context):
    subjects = set(jsonutils.load(event["body"])["subjects"])

    return {
        "statusCode": HTTPStatus.OK,
        "body": jsonutils.dump(
            {k: v.to_json() for k, v in
             get_performance_summary_for_subjects(subjects, performance_core.calculate_portfolio_summary).items()}
        )
    }
