from datetime import datetime
from typing import Optional

from aws_lambda_powertools import Logger

from application.exceptions import (
    InvalidInvestmentDateError,
    FieldNotPermittedError,
    FieldMissingError, InvalidTicker,
)
from application.investment import StockInvestment
from application.investment_loader import load_model_by_type
from application.investment_request import InvestmentRequest
from application.paginated_investments_result import PaginatedInvestmentsResult
from application.ports.outbound.investment_repository import InvestmentRepository
from application.ports.outbound.ticker_info_client import TickerInfoClient

logger = Logger()


class InvestmentCore:
    def __init__(self, repo: InvestmentRepository, ticker: TickerInfoClient):
        self.repo = repo
        self.ticker_client = ticker

    def validate_investment(self, investment):
        if investment.date > datetime.now().date():
            raise InvalidInvestmentDateError()
        if type(investment) == StockInvestment:
            if not self.ticker_client.is_ticker_valid(investment.ticker):
                raise InvalidTicker(f"Ativo {investment.ticker} invalido.")

    def get(
            self,
            subject: str,
            limit: Optional[int] = None,
            last_evaluated_id: Optional[str] = None,
            last_evaluated_date: Optional[datetime.date] = None,
            ticker: Optional[str] = None
    ):
        investments, new_last_evaluated_id, new_last_evaluated_date = self.repo.find_by_subject(
            subject,
            ticker,
            limit,
            last_evaluated_id,
            last_evaluated_date
        )
        if not limit:
            return investments
        return PaginatedInvestmentsResult(
            investments=investments,
            last_evaluated_id=new_last_evaluated_id,
            last_evaluated_date=new_last_evaluated_date
        )

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
            investments.append(investment)
        self.repo.batch_save(investments)
