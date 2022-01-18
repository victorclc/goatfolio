import datetime
import logging

from dateutil.relativedelta import relativedelta

from adapters.inbound import ticker_client, events_repo, events_client
from adapters.outbound.sqs_new_applicable_events_notifier import SQSNewApplicableEventsNotifier
from application.enums.event_type import EventType
from core.fetch_today_corporate_events import fetch_today_corporate_events
from core.handle_corporate_events import handle_corporate_events
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def craw_today_corporate_events_handler(event, context):
    fetch_today_corporate_events(events_client, ticker_client, events_repo)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_yesterday_split_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    notifier = SQSNewApplicableEventsNotifier()
    handle_corporate_events(EventType.SPLIT, yesterday, events_repo, notifier)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_yesterday_group_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    notifier = SQSNewApplicableEventsNotifier()
    handle_corporate_events(EventType.GROUP, yesterday, events_repo, notifier)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_yesterday_incorporation_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    notifier = SQSNewApplicableEventsNotifier()
    handle_corporate_events(EventType.INCORPORATION, yesterday, events_repo, notifier)
