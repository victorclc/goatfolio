from datetime import datetime
from uuid import uuid4

from adapters import InvestmentRepository
from goatcommons.utils import InvestmentUtils
from model import InvestmentRequest


class InvestmentCore:
    def __init__(self):
        self.repo = InvestmentRepository()

    def get(self, subject, query_params):
        assert subject
        if query_params and 'date' in query_params:
            data = query_params['date'].split('.')
            assert len(data) == 2, 'invalid query param'
            operand = data[0]
            value = int(data[1])
            assert operand in ['gt', 'ge', 'lt', 'le', 'eq']
            return self.repo.find_by_subject_and_date(subject, operand, value)
        return self.repo.find_by_subject(subject)

    def add(self, subject, request: InvestmentRequest):
        assert subject
        investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
        assert investment.date <= datetime.now(), 'invalid date'
        investment.id = str(uuid4())
        investment.subject = subject

        self.repo.save(investment)
        return investment

    def edit(self, subject, request: InvestmentRequest):
        assert subject
        investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
        investment.subject = subject
        assert investment.id, 'investment id is empty'
        assert investment.date <= datetime.now(), 'invalid date'

        self.repo.save(investment)
        return investment

    def delete(self, subject, investment_id):
        assert subject
        assert investment_id, 'investment id is empty'

        self.repo.delete(investment_id, subject)

    def batch_add(self, requests: [InvestmentRequest]):
        investments = []
        for request in requests:
            investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
            assert investment.subject, 'subject is empty'
            assert investment.id, 'investment id is empty'

            investments.append(investment)
        self.repo.batch_save(investments)
