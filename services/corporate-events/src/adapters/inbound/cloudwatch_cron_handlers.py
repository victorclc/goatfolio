import datetime
import logging

from dateutil.relativedelta import relativedelta

from domain.core.corporate_events_core import CorporateEventsCore
from domain.core.corporate_events_crawler import B3CorporateEventsCrawler
from domain.enums.event_type import EventType
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel
import domain.core.strategy as strategies

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


core = CorporateEventsCore()


@notify_exception(Exception, NotifyLevel.CRITICAL)
def craw_today_corporate_events_handler(event, context):
    today = datetime.datetime.now().date()
    crawler = B3CorporateEventsCrawler()

    crawler.craw_corporate_events_from_date(today)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_yesterday_split_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    core.handle_corporate_events(
        EventType.SPLIT, yesterday, strategies.handle_split_event_strategy
    )


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_today_group_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    core.handle_corporate_events(
        EventType.GROUP, yesterday, strategies.handle_group_event_strategy
    )


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_today_incorporation_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    core.handle_corporate_events(
        EventType.INCORPORATION,
        yesterday,
        strategies.handle_incorporation_event_strategy,
    )
