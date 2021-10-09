from datetime import datetime

from aws_lambda_powertools import Logger

from domain.exceptions import (
    InvalidInvestmentDateError,
    FieldNotPermittedError,
    FieldMissingError,
)
from domain.investment import Investment
from domain.investment_loader import load_model_by_type
from domain.investment_request import InvestmentRequest
from ports.outbound.investment_publisher import InvestmentPublisher
from ports.outbound.investment_repository import InvestmentRepository

logger = Logger()


class InvestmentCore:
    def __init__(self, repo: InvestmentRepository, publisher: InvestmentPublisher):
        self.repo = repo
        self.publisher = publisher

    @staticmethod
    def validate_investment(investment):
        if investment.date > datetime.now().date():
            raise InvalidInvestmentDateError()

    def get(self, subject: str):
        return self.repo.find_by_subject(subject)

    def add(self, subject: str, request: InvestmentRequest):
        if request.investment.get("id"):
            raise FieldNotPermittedError("id field not permitted")

        request.investment["subject"] = subject
        investment = load_model_by_type(request.type, request.investment)
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
        new_investment: Investment,
        old_investment: Investment,
    ):
        logger.info(
            f"Publishing: subject={subject}, new_investment={new_investment}, old_investment{old_investment}"
        )
        self.publisher.publish(
            subject, new_investment=new_investment, old_investment=old_investment
        )
