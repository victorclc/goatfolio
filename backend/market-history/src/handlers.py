from core import CotaHistTransformerCore, CotaHistDownloaderCore
import goatcommons.utils.json as jsonutils
from event_notifier.decorators import notify_exception

from aws_lambda_powertools import Logger, Tracer

from event_notifier.models import NotifyLevel

logger = Logger()
tracer = Tracer()


@notify_exception(Exception, notify_level=NotifyLevel.ERROR)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def transform_cota_hist_handler(event, context):
    logger.info(f"EVENT: {event}")
    core = CotaHistTransformerCore()
    for record in event["Records"]:
        logger.info(f"Processing record: {record}")
        bucket = record["s3"]["bucket"]["name"]
        file_path = record["s3"]["object"]["key"]
        core.transform_cota_hist(bucket, file_path)


@notify_exception(Exception, notify_level=NotifyLevel.ERROR)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def ibov_history_handler(event, context):
    logger.info(f"EVENT: {event}")
    core = CotaHistTransformerCore()
    core.update_ibov_history()


@notify_exception(Exception, notify_level=NotifyLevel.ERROR)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def download_current_monthly_cotahist_file(event, context):
    core = CotaHistDownloaderCore()
    core.download_current_monthly_file()


@notify_exception(Exception, notify_level=NotifyLevel.ERROR)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def download_monthly_cotahist_file(event, context):
    body = jsonutils.load(event["body"])
    core = CotaHistDownloaderCore()
    core.download_monthly_file(body["year"], body["month"])
