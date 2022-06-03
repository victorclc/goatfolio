from decimal import Decimal
from itertools import groupby
from typing import Protocol, List, Optional, Dict, Any, Tuple

from aws_lambda_powertools import Logger

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from application.models.dividends import CashDividends
from application.models.invesments import StockInvestment, OperationType, StockDividend

logger = Logger()


class CorporateEventsClient(Protocol):
    def get_all_previous_symbols(self, isin_code: str) -> List[str]:
        ...


class TickerInfoClient(Protocol):
    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        ...


def calculate_investments_amount(investments: List[StockInvestment]) -> Decimal:
    amount = Decimal(0)
    for inv in investments:
        if inv.operation in [
            OperationType.BUY,
            OperationType.SPLIT,
            OperationType.INCORP_ADD,
        ]:
            amount = amount + inv.amount
        else:
            amount = amount - inv.amount
    return amount


class CashDividendsEarningsCalculator:
    def __init__(
            self,
            events_client: CorporateEventsClient,
            ticker_client: TickerInfoClient,
            investments_repository: DynamoInvestmentRepository
    ):
        self.events_client = events_client
        self.ticker_client = ticker_client
        self.investments_repository = investments_repository

    def get_applicable_investments_for_cash_dividend(
            self,
            dividend: CashDividends,
            subject: Optional[str] = None
    ) -> List[StockInvestment]:
        all_isin_symbols = self.events_client.get_all_previous_symbols(dividend.asset_issued) + [dividend.asset_issued]
        tickers = list(
            filter(lambda i: i, map(lambda i: self.ticker_client.get_ticker_from_isin_code(i), all_isin_symbols))
        )
        logger.info(f"All tickers related to {dividend.asset_issued}: {tickers}")

        investments = []
        for ticker in tickers:
            investments += self.investments_repository.find_by_ticker_until_date(
                ticker, dividend.last_date_prior, subject
            )
        return investments

    def calculate_earnings_of_cash_dividend_for_subject(
            self,
            subject: str,
            dividend: CashDividends
    ) -> StockDividend:
        investments = self.get_applicable_investments_for_cash_dividend(dividend, subject)
        ticker = self.ticker_client.get_ticker_from_isin_code(dividend.asset_issued)
        logger.info(f"Found {len(investments)} applicable investments for {subject}.")
        amount = calculate_investments_amount(investments)

        sd = StockDividend(
            ticker,
            dividend.label,
            self.calculate_payed_amount(amount, dividend),
            subject,
            dividend.payment_date,
            f"STOCK_DIVIDEND#{ticker}#{dividend.asset_issued}#{dividend.id}#{dividend.isin_code}"
        )

        return sd

    def calculate_earnings_of_cash_dividend_for_all_users(self, dividend: CashDividends) -> List[StockDividend]:
        investments = self.get_applicable_investments_for_cash_dividend(dividend)
        ticker = self.ticker_client.get_ticker_from_isin_code(dividend.asset_issued)
        logger.info(f"Found {len(investments)} applicable investments.")

        earnings = []
        for subject, sub_investments in groupby(sorted(investments, key=lambda i: i.subject), key=lambda i: i.subject):
            amount = calculate_investments_amount(list(sub_investments))
            if amount > 0:
                earnings.append(
                    StockDividend(
                        ticker,
                        dividend.label,
                        self.calculate_payed_amount(amount, dividend),
                        subject,
                        dividend.payment_date,
                        f"STOCK_DIVIDEND#{ticker}#{dividend.asset_issued}#{dividend.id}#{dividend.isin_code}"
                    )
                )
        return earnings

    @staticmethod
    def calculate_payed_amount(amount: Decimal, dividend: CashDividends):
        tax = Decimal(1)
        if dividend.label == "JRS CAP PROPRIO":
            tax = Decimal(0.85)
        return (amount * dividend.rate * tax).quantize(Decimal("0.01"))
