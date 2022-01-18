from datetime import datetime

from aws_lambda_powertools import Logger

from application.enums.event_type import EventType
from application.ports.corporate_events_repository import CorporateEventsRepository
from core.add_manual_corporate_events import NewEventNotifier

logger = Logger()


def handle_corporate_events(
        event_type: EventType,
        date: datetime.date,
        repository: CorporateEventsRepository,
        notifier: NewEventNotifier

):
    events = repository.find_by_type_and_date(event_type, date)
    logger.info(f"Events to process: {events}")
    for event in events:
        logger.info(f"Processing event: {event}")
        notifier.notify(event)
