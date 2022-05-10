from datetime import datetime
from typing import Protocol, List, Set, Optional

from aws_lambda_powertools import Logger

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from application.models.add_investment_request import AddInvestmentRequest
from application.models.dividends import CashDividends
from application.models.invesments import StockInvestment, StockDividend, InvestmentType
from core.calculators import CashDividendsEarningsCalculator, CorporateEventsClient, TickerInfoClient

logger = Logger()


class CashDividendsClient(Protocol):
    def get_cash_dividends_for_ticker(
            self, ticker: str, from_date: datetime.date
    ) -> List[CashDividends]:
        ...


class InvestmentsClient(Protocol):
    def delete(self, subject: str, _id: str):
        ...

    def batch_save(self, requests: List[AddInvestmentRequest]):
        ...


class NewInvestmentsConsumer:
    def __init__(
            self,
            dividends_client: CashDividendsClient,
            corporate_events_client: CorporateEventsClient,
            ticker_info_client: TickerInfoClient,
            investments_repository: DynamoInvestmentRepository,
            investments_client: InvestmentsClient
    ):
        self.investments_client = investments_client
        self.investments_repository = investments_repository
        self.ticker_info_client = ticker_info_client
        self.corporate_events_client = corporate_events_client
        self.dividends_client = dividends_client
        self.helper = CashDividendsEarningsCalculator(corporate_events_client, ticker_info_client, investments_repository)

    def receive(
            self,
            subject: str,
            new_investment: Optional[StockInvestment],
            old_investment: Optional[StockInvestment]
    ):
        if self.is_edit_of_investment(new_investment, old_investment) \
                and not self.has_dividends_affected_changes(new_investment, old_investment):
            logger.info("No dividend related info edited, nothing to do.")
            return

        if new_investment:
            self.handle_applicable_cash_dividends(subject, new_investment)
        if old_investment:
            self.handle_applicable_cash_dividends(subject, old_investment)

    def handle_applicable_cash_dividends(self, subject: str, investment: StockInvestment):
        logger.info(f"Handle applicable cash dividends for {investment}")
        dividends = list(filter(
            lambda c: c.payment_date <= datetime.now().date(),
            self.dividends_client.get_cash_dividends_for_ticker(investment.ticker, investment.date)
        ))
        logger.info(f"Found {len(dividends)} applicable dividends")

        payouts = []
        for dividend in dividends:
            ticker, earnings = self.helper.calculate_earnings_of_cash_dividend_for_subject(subject, dividend)
            _id = f"STOCK_DIVIDEND#{dividend.id}"
            if earnings > 0:
                sd = StockDividend(ticker, dividend.label, earnings, subject, dividend.payment_date, _id)
                logger.debug(f"Generated StockDividend: {sd}")
                payouts.append(sd)
            else:
                logger.info(f"Dividend not applicable, deleting. sub: {subject}, id: {_id}")
                self.investments_client.delete(subject, _id)

        if payouts:
            self.investments_client.batch_save(
                [
                    AddInvestmentRequest(
                        type=InvestmentType.STOCK_DIVIDEND,
                        investment=s.to_json(),
                        subject=subject
                    ) for s in payouts
                ]
            )

    @staticmethod
    def is_edit_of_investment(new_investment, old_investment):
        return new_investment and old_investment

    @staticmethod
    def has_dividends_affected_changes(new_investment, old_investment):
        return new_investment.ticker != old_investment.ticker \
               or new_investment.alias_ticker != old_investment.alias_ticker \
               or new_investment.date != old_investment.date \
               or new_investment.amount != old_investment.amount
