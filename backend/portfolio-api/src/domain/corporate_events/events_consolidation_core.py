from itertools import groupby
from typing import List

from domain.common.investments import Investment, StockInvestment
from domain.corporate_events.events_consolidation_strategies import HandleEventStrategy
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

    @staticmethod
    def get_alias_ticker(investments: List[StockInvestment]):
        for investment in investments:
            if investment.alias_ticker:
                return investment.alias_ticker

    def check_for_applicable_corporate_events(
            self,
            subject: str,
            investments: List[StockInvestment],
            handle_event_strategy: HandleEventStrategy,
    ):
        # TODO PRECISA DAR UM JEITO DE PASSAR PELO TICKER E ALIAS TICKER
        investments_map = groupby(
            sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker
        )
        for ticker, investments in investments_map:
            investments = list(investments)
            oldest = min([i.date for i in investments])
            logger.info(f"Processing {ticker}: {investments}")

            events = self.events_client.corporate_events_from_date(subject, ticker, oldest)
            alias_ticker = self.get_alias_ticker(investments)
            if alias_ticker:
                logger.info(f"Searching events for alias_ticker {alias_ticker}.")
                events += self.events_client.corporate_events_from_date(subject, alias_ticker, oldest)
            if not events:
                logger.info(f"No applicable event for {ticker} on {oldest.strftime('%Y-%m-%d')}")
                continue

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
                logger.info(f"len(affected_investment) is {len(affected_investments)}")

                new_investments = handle_event_strategy(
                    subject, ticker, event, list(affected_investments)
                )
                logger.info(f"new_investments: {new_investments}")
                if new_investments:
                    self.investments.batch_save(new_investments)
