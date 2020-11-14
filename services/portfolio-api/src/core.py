from uuid import uuid4

from adapters import InvestmentRepository
from exceptions import BadRequestException
from goatcommons.utils import InvestmentUtils
from model import InvestmentRequest


class InvestmentCore:
    def __init__(self):
        self.repo = InvestmentRepository()

    def get_all(self, subject):
        return self.repo.find_by_subject(subject)

    def add(self, subject, request: InvestmentRequest):
        try:
            investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
            investment.id = str(uuid4())
            investment.subject = subject

            self.repo.save(investment)
        except TypeError:
            raise BadRequestException("Invalid request")

    def edit(self, subject, request: InvestmentRequest):
        try:
            investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
            investment.subject = subject

            self.repo.save(investment)
        except TypeError:
            raise BadRequestException("Invalid request")

    def delete(self, subject, investment_id):
        self.repo.delete(investment_id, subject)
