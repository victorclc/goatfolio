from datetime import datetime, timezone
from uuid import uuid4

from domain.ports.out.investment_repository import InvestmentRepository
from goatcommons.utils import InvestmentUtils
from domain.models.investment_request import InvestmentRequest


class InvestmentCore:
    def __init__(self, repo: InvestmentRepository):
        self.repo = repo

    def get(self, subject):
        return self.repo.find_by_subject(subject)

    def add(self, subject, request: InvestmentRequest):
        # TODO REFACTOR THIS
        investment = InvestmentUtils.load_model_by_type(
            request.type, request.investment
        )
        assert investment.date <= datetime.now(tz=timezone.utc), "invalid date"
        if not investment.id:
            investment.id = str(uuid4())
        investment.subject = subject

        self.repo.save(investment)
        return investment

    def edit(self, subject, request: InvestmentRequest):
        assert subject
        investment = InvestmentUtils.load_model_by_type(
            request.type, request.investment
        )
        investment.subject = subject
        assert investment.id, "investment id is empty"
        assert investment.date <= datetime.now(tz=timezone.utc), "invalid date"

        self.repo.save(investment)
        return investment

    def delete(self, subject, investment_id):
        assert subject
        assert investment_id, "investment id is empty"

        self.repo.delete(investment_id, subject)

    def batch_add(self, requests: [InvestmentRequest]):
        investments = []
        for request in requests:
            investment = InvestmentUtils.load_model_by_type(
                request.type, request.investment
            )
            assert investment.subject, "subject is empty"
            assert investment.id, "investment id is empty"

            investments.append(investment)
        self.repo.batch_save(investments)
