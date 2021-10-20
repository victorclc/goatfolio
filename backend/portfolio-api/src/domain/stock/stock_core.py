import datetime as dt
from decimal import Decimal
from uuid import uuid4

from domain.common.investment_consolidated import StockConsolidated
from domain.common.investments import OperationType, StockInvestment
from ports.outbound.investment_repository import InvestmentRepository
from ports.outbound.portfolio_repository import PortfolioRepository
from ports.outbound.corporate_events_client import (
    CorporateEventsClient,
)


class StockCore:
    """Stock only specific endpoints"""

    def __init__(
        self,
        portfolio: PortfolioRepository,
        investments: InvestmentRepository,
        transformation_client: CorporateEventsClient,
    ):
        self.portfolio = portfolio
        self.investments = investments
        self.transformation_client = transformation_client

    def average_price_fix(
        self,
        subject: str,
        ticker: str,
        date: dt.date,
        broker: str,
        amount: Decimal,
        average_price: Decimal,
    ):
        # TODO VALIDAR PRECO NEGATIVO
        consolidated = self.get_stock_consolidated(subject, ticker)
        transformation = self.transformation_client.get_ticker_transformation(
            ticker, date
        )
        i_amount = amount / transformation.grouping_factor
        price = self.calculate_new_investment_price(
            consolidated, i_amount, average_price
        )

        investment = self.create_stock_investment(
            subject,
            date,
            broker,
            transformation.ticker,
            i_amount,
            price,
        )
        self.investments.save(investment)

        return investment

    def get_stock_consolidated(self, subject, ticker):
        consolidations = self.portfolio.find_alias_ticker(
            subject, ticker, StockConsolidated
        )
        return sum(consolidations[1:], consolidations[0])

    @staticmethod
    def create_stock_investment(subject, date, broker, ticker, amount, price):
        return StockInvestment(
            subject,
            str(uuid4()),
            date,
            OperationType.BUY,
            broker,
            ticker,
            amount,
            price,
        )

    @staticmethod
    def calculate_new_investment_price(
        consolidated: StockConsolidated, amount: Decimal, average_price: Decimal
    ) -> Decimal:
        wrappers = consolidated.monthly_stock_position_wrapper_linked_list()

        current_invested = wrappers.tail.current_invested_value
        new_invested = (wrappers.tail.amount + amount) * average_price

        return ((new_invested - current_invested) / amount).quantize(Decimal("0.01"))
