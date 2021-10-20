from itertools import groupby
from typing import List

from domain.common.investments import Investment
from domain.portfolio.events_consolidation_strategies import HandleEventStrategy
from ports.outbound.corporate_events_client import CorporateEventsClient
from ports.outbound.investment_repository import InvestmentRepository

from aws_lambda_powertools import Logger

logger = Logger()


class CorporateEventsConsolidationCore:
    def __init__(
        self, investments: InvestmentRepository, events: CorporateEventsClient
    ):
        self.investments = investments
        self.events_client = events

    def check_for_applicable_corporate_events_handler(
        self,
        subject: str,
        investments: List[Investment],
        handle_event_strategy: HandleEventStrategy,
    ):
        investments_map = groupby(
            sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker
        )
        for ticker, investments in investments_map:
            investments = list(investments)
            oldest = min([i.date for i in investments])

            events = self.events_client.corporate_events_from_date(ticker, oldest)

            all_ticker_investments = self.investments.find_by_subject_and_ticker(
                subject, ticker
            )
            for event in events:
                logger.info(f"Handling event {event} for {subject}")
                affected_investments = list(
                    filter(
                        lambda i, with_date=event.with_date: i.date <= with_date,
                        all_ticker_investments,
                    )
                )

                new_investments = handle_event_strategy(
                    subject, ticker, event, list(affected_investments)
                )
                if new_investments:
                    self.investments.batch_save(new_investments)
