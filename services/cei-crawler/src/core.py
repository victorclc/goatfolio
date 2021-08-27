import logging
import os
import re
import traceback
import uuid
from datetime import datetime
from decimal import Decimal

from selenium import webdriver

from adapters import CEIResultQueue
from constants import ImportStatus
from exceptions import LoginError
from goatcommons.models import StockInvestment
from goatcommons.shit.client import ShitNotifierClient
from goatcommons.shit.models import NotifyLevel
from goatcommons.utils import JsonUtils
from lessmium.webdriver import LessmiumDriver
from models import CEICrawRequest, CEICrawResult
from pages import LoginPage

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CEICrawlerCore:
    LOGIN_URL = os.getenv("LOGIN_URL")
    EXTRACT_DATE_FORMAT = '%d/%m/%Y'

    def __init__(self, queue=None):
        self._driver = None
        self.queue = queue or CEIResultQueue()

        self.identifiers = set()

    @property
    def driver(self):
        if not self._driver:
            self._driver = LessmiumDriver()
        return self._driver

    def craw_all_extract(self, request: CEICrawRequest):
        response = CEICrawResult(subject=request.subject, datetime=request.datetime)
        try:
            login_page = LoginPage(self.driver, request.credentials.tax_id, request.credentials.password)
            home_page = login_page.login()
            extract_page = home_page.go_to_extract_page()

            investments = self._extract_to_investments(request.subject, extract_page.get_all_brokers_extract())

            response.status = ImportStatus.SUCCESS
            response.payload = investments
        except LoginError as e:
            logger.exception('Invalid login credentials')
            response.status = ImportStatus.ERROR
            response.login_error = True
            response.payload = JsonUtils.dump({"error_message": str(e)})
        except Exception as e:
            traceback.print_exc()
            ShitNotifierClient().send(NotifyLevel.ERROR, 'CEI-CRAWLER',
                                      f'CRAW ALL EXTRACT FAILED {traceback.format_exc()}')
            response.status = ImportStatus.ERROR
            response.payload = JsonUtils.dump({"error_message": str(e)})
        self.queue.send(response)
        self._cleanup()

    def _cleanup(self):
        # fixed a weird bug where lambda used the exact same instance of this class on the next processing
        self.identifiers = set()

    def _extract_to_investments(self, subject, extract):
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
                                broker=investment['corretora'], external_system='CEI', subject=subject)
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


if __name__ == '__main__':
    driver = webdriver.Chrome()
    login_page = LoginPage(driver, '23011337888', '%wMepyO97Jlac')
    home_page = login_page.login()
    extract_page = home_page.go_to_asset_inquiry_page()
    investments = []
    for investment in extract_page.get_assets_quantity():
        if not investment['quantidade']:
            continue
        s = StockInvestment(type='STOCK',
                            operation='BUY' if investment['compra_venda'] == 'C' else 'SELL',
                            ticker=re.sub('F$', '', investment['codigo_negociacao']),
                            amount=Decimal(investment['quantidade']),
                            price=Decimal(investment['preco']),
                            date=datetime.strptime(investment['data_do_negocio'], '%d/%m/%Y'),
                            broker=investment['corretora'], external_system='CEI', subject='12345')
        s.id = uuid.uuid4()
        investments.append(s)
    print(investments)
