import datetime
import logging

from dateutil.relativedelta import relativedelta

import domain.core.strategy as strategies
from adapters.inbound import corporate_events_crawler, corporate_events_core
from domain.enums.event_type import EventType
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def craw_today_corporate_events_handler(event, context):
    today = datetime.datetime.now().date()

    corporate_events_crawler.craw_corporate_events_from_date(today)


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_yesterday_split_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    corporate_events_core.handle_corporate_events(
        EventType.SPLIT, yesterday, strategies.handle_split_event_strategy
    )


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_today_group_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    corporate_events_core.handle_corporate_events(
        EventType.GROUP, yesterday, strategies.handle_group_event_strategy
    )


@notify_exception(Exception, NotifyLevel.CRITICAL)
def handle_today_incorporation_events_handler(event, context):
    yesterday = datetime.datetime.now().date() - relativedelta(days=1)
    corporate_events_core.handle_corporate_events(
        EventType.INCORPORATION,
        yesterday,
        strategies.handle_incorporation_event_strategy,
    )


def main():
    date_from = datetime.datetime.now().date() - relativedelta(months=18)
    print(corporate_events_core.transformations_in_ticker("AESB3", date_from))


if __name__ == "__main__":
    main()
