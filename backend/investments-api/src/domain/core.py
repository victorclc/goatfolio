from datetime import datetime

from aws_lambda_powertools import Logger

from domain.exceptions import (
    InvalidInvestmentDateError,
    FieldNotPermittedError,
    FieldMissingError, InvalidTicker,
)
from domain.investment import Investment, StockInvestment
from domain.investment_loader import load_model_by_type
from domain.investment_request import InvestmentRequest
from ports.outbound.investment_publisher import InvestmentPublisher
from ports.outbound.investment_repository import InvestmentRepository
from ports.outbound.ticker_info_client import TickerInfoClient

logger = Logger()


class InvestmentCore:
    def __init__(self, repo: InvestmentRepository, publisher: InvestmentPublisher, ticker: TickerInfoClient):
        self.repo = repo
        self.publisher = publisher
        self.ticker_client = ticker

    def validate_investment(self, investment):
        if investment.date > datetime.now().date():
            raise InvalidInvestmentDateError()
        if type(investment) == StockInvestment:
            if not self.ticker_client.is_ticker_valid(investment.ticker):
                raise InvalidTicker(f"Ativo {investment.ticker} invalido.")

    def get(self, subject: str):
        return self.repo.find_by_subject(subject)

    def add(self, subject: str, request: InvestmentRequest):
        if request.investment.get("id"):
            raise FieldNotPermittedError("id field not permitted")

        request.investment["subject"] = subject
        investment = load_model_by_type(request.type, request.investment, generate_id=True)
        self.validate_investment(investment)

        self.repo.save(investment)

        return investment

    def edit(self, subject: str, request: InvestmentRequest):
        if not request.investment.get("id"):
            raise FieldMissingError("id field is missing")

        request.investment["subject"] = subject
        investment = load_model_by_type(
            request.type, request.investment, generate_id=False
        )
        self.validate_investment(investment)
        self.repo.save(investment)

        return investment

    def delete(self, subject: str, investment_id: str):
        if not investment_id:
            raise FieldMissingError("ID is missing.")

        self.repo.delete(investment_id, subject)

    def batch_add(self, requests: [InvestmentRequest]):
        investments = []
        for request in requests:
            investment = load_model_by_type(
                request.type, request.investment, generate_id=False
            )
            if not investment.subject:
                raise FieldMissingError("Subject is missing.")

            investments.append(investment)
        self.repo.batch_save(investments)

    def publish_investment_update(
        self,
        subject: str,
        updated_timestamp: int,
        new_investment: Investment,
        old_investment: Investment
    ):
        logger.info(
            f"Publishing: subject={subject}, new_investment={new_investment}, old_investment{old_investment}"
        )
        self.publisher.publish(
            subject, updated_timestamp, new_investment=new_investment, old_investment=old_investment
        )
