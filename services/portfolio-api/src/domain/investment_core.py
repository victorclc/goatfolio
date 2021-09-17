from datetime import datetime, timezone
from uuid import uuid4

from domain.ports.outbound.investment_repository import InvestmentRepository
from domain.utils.investment_loader import load_model_by_type
from domain.models.investment_request import InvestmentRequest


class InvestmentCore:
    def __init__(self, repo: InvestmentRepository):
        self.repo = repo

    def get(self, subject: str):
        return self.repo.find_by_subject(subject)

    def add(self, subject: str, request: InvestmentRequest):
        # TODO REFACTOR THIS
        investment = load_model_by_type(
            request.type, request.investment
        )
        assert investment.date <= datetime.now(tz=timezone.utc), "invalid date"
        if not investment.id:
            investment.id = str(uuid4())
        investment.subject = subject

        self.repo.save(investment)
        return investment

    def edit(self, subject: str, request: InvestmentRequest):
        assert subject
        investment = load_model_by_type(
            request.type, request.investment
        )
        investment.subject = subject
        assert investment.id, "investment id is empty"
        assert investment.date <= datetime.now(tz=timezone.utc), "invalid date"

        self.repo.save(investment)
        return investment

    def delete(self, subject: str, investment_id: str):
        assert subject
        assert investment_id, "investment id is empty"

        self.repo.delete(investment_id, subject)

    def batch_add(self, requests: [InvestmentRequest]):
        investments = []
        for request in requests:
            investment = load_model_by_type(
                request.type, request.investment
            )
            assert investment.subject, "subject is empty"
            assert investment.id, "investment id is empty"

            investments.append(investment)
        self.repo.batch_save(investments)
