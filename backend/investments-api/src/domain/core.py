from datetime import datetime

from domain.investment_loader import load_model_by_type
from domain.investment_request import InvestmentRequest
from ports.outbound.investment_repository import InvestmentRepository


# TODO CUSTOM EXCEPTIONS INSTEAD OF ASSERT


class InvestmentCore:
    def __init__(self, repo: InvestmentRepository):
        self.repo = repo

    def get(self, subject: str):
        return self.repo.find_by_subject(subject)

    def add(self, subject: str, request: InvestmentRequest):
        request.investment['subject'] = subject
        investment = load_model_by_type(request.type, request.investment)
        assert investment.date <= datetime.now().date(), "invalid date"
        investment.subject = subject

        self.repo.save(investment)
        return investment

    def edit(self, subject: str, request: InvestmentRequest):
        assert subject
        request.investment['subject'] = subject
        investment = load_model_by_type(request.type, request.investment, generate_id=False)
        assert investment.date <= datetime.now().date(), "invalid date"

        self.repo.save(investment)
        return investment

    def delete(self, subject: str, investment_id: str):
        assert subject
        assert investment_id, "investment id is empty"

        self.repo.delete(investment_id, subject)

    def batch_add(self, requests: [InvestmentRequest]):
        investments = []
        for request in requests:
            investment = load_model_by_type(request.type, request.investment, generate_id=False)
            assert investment.subject, "subject is empty"

            investments.append(investment)
        self.repo.batch_save(investments)
