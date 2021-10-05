import logging

from adapters.inbound import corporate_events_file_processor
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def process_corporate_events_file_handler(event, context):
    logger.info(f"EVENT: {event}")

    for record in event["Records"]:
        logger.info(f"Processing record: {record}")
        bucket = record["s3"]["bucket"]["name"]
        file_path = record["s3"]["object"]["key"]
        corporate_events_file_processor.process_corporate_events_file(bucket, file_path)
