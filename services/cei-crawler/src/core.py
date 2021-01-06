import logging
import re
from datetime import datetime
from decimal import Decimal

from adapters import CEIResultQueue
from constants import ImportStatus
from goatcommons.models import StockInvestment
from goatcommons.utils import JsonUtils
from lessmium.webdriver import LessmiumDriver
from models import CEICrawRequest, CEICrawResult
from pages import LoginPage

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CEICrawlerCore:
    LOGIN_URL = "https://ceiapp.b3.com.br/CEI_Responsivo/login.aspx"  # TODO put on an environment variable
    EXTRACT_DATE_FORMAT = '%d/%m/%Y'

    def __init__(self, queue=CEIResultQueue()):
        self.driver = LessmiumDriver()
        self.queue = queue
        self.identifiers = set()

    def craw_all_extract(self, request: CEICrawRequest):
        response = CEICrawResult(subject=request.subject, datetime=request.datetime)
        try:
            login_page = LoginPage(self.driver, request.credentials.tax_id, request.credentials.password)
            home_page = login_page.login()
            extract_page = home_page.go_to_extract_page()

            investments = self._extract_to_investments(extract_page.get_all_brokers_extract())

            response.status = ImportStatus.SUCCESS
            response.payload = investments
        except Exception as e:
            logger.exception('CAUGHT EXCEPTION')
            response.status = ImportStatus.ERROR
            response.payload = JsonUtils.dump({"error_message": str(e)})
        self.queue.send(response)

    def _extract_to_investments(self, extract):
        investments = []
        for investment in extract:
            if not investment['quantidade']:
                continue
            s = StockInvestment(type='STOCK',
                                operation='BUY' if investment['compra_venda'] == 'C' else 'SELL',
                                ticker=re.sub('F$', '', investment['codigo_negociacao']),
                                amount=Decimal(investment['quantidade']),
                                price=Decimal(investment['preco']),
                                date=datetime.strptime(investment['data_do_negocio'], self.EXTRACT_DATE_FORMAT),
                                broker=investment['corretora'], external_system='CEI')
            s.id = self._generate_id(s)
            investments.append(s)
        return investments

    def _generate_id(self, s):
        counter = 0
        _id = None

        while not _id or _id in self.identifiers:
            counter = counter + 1
            _id = f'CEI{s.ticker}{int(s.date.timestamp())}{s.amount}{str(s.price).replace(".", "")}{counter}'
        self.identifiers.add(_id)
        return _id
