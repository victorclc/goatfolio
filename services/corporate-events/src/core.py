import logging
import math
import traceback
from datetime import datetime
from decimal import Decimal
from io import StringIO
from itertools import groupby
from typing import List

import pandas as pd
from dateutil.relativedelta import relativedelta

from adapters import B3CorporateEventsData, B3CorporateEventsBucket, CorporateEventsRepository, InvestmentRepository, \
    AsyncPortfolioQueue, TickerInfoRepository
from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment
from model import EarningsInAssetCorporateEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CorporateEventsCrawlerCore:
    def __init__(self):
        self.b3 = B3CorporateEventsData()
        self.bucket = B3CorporateEventsBucket()
        self.repo = CorporateEventsRepository()

    def download_today_corporate_events(self):
        today = datetime.now().date()
        companies_data = self.b3.get_updated_corporate_events_link(today)
        for data in companies_data:
            if 'fundsPage' in data.url:
                logger.info(f'Skipping funds page: {data.url}')
                continue
            attempts = 0
            while attempts < 3:
                logger.info(f'Processing (attempt {attempts}: {data.url}')
                try:
                    tables = pd.read_html(data.url)
                    count = 0
                    for table in tables:
                        csv_name = f'{data.code_cvm}-{today.strftime("%Y%m%d")}-{count}.csv'
                        csv_buffer = StringIO()
                        table.to_csv(csv_buffer)
                        self.bucket.put(csv_buffer, csv_name)
                        count = count + 1
                    break
                except Exception:
                    logger.warning(f'Attempt {attempts} failed.')
                    traceback.print_exc()
                attempts = attempts + 1
        logger.info(f'Processing finish')

    def process_corporate_events_file(self, bucket_name, file_path):
        downloaded_path = self.bucket.download_file(bucket_name, file_path)
        table = pd.read_csv(downloaded_path)

        if set(table.columns) == {'Unnamed: 0', 'Proventos', 'Código ISIN', 'Deliberado em',
                                  'Negócios com até', '% / Fator de Grupamento', 'Ativo Emitido',
                                  'Observações'}:
            table.drop('Unnamed: 0', inplace=True, axis=1)
            table.columns = ['type', 'isin_code', 'deliberate_on', 'with_date', 'grouping_factor', 'emitted_asset',
                             'observations']

            records = table.to_dict('records')
            for record in records:
                record['with_date'] = datetime.strptime(record['with_date'], '%d/%m/%Y').strftime('%Y%m%d')
                record['deliberate_on'] = datetime.strptime(record['deliberate_on'], '%d/%m/%Y').strftime('%Y%m%d')
            self.repo.batch_save([EarningsInAssetCorporateEvent(**row) for row in records])

        self.bucket.move_file_to_archive(bucket_name, file_path)
        self.bucket.clean_up()


class CorporateEventsCore:
    def __init__(self):
        self.repo = CorporateEventsRepository()
        self.ticker_info = TickerInfoRepository()
        self.investments_repo = InvestmentRepository()
        self.async_portfolio = AsyncPortfolioQueue()

    def handle_today_corporate_events(self):
        # check all querys IAM permissions
        yesterday = datetime.now() - relativedelta(days=1)
        events = self.repo.events_on_date('DESDOBRAMENTO', yesterday)
        events += self.repo.events_on_date('GRUPAMENTO', yesterday)
        events += self.repo.events_on_date('INCORPORACAO', yesterday)

        logger.info(f'Today corporate events: {events}')
        for event in events:
            logger.info(f'Processing event: {event}')
            ticker = self.ticker_info.ticker_from_isin_code(event.isin_code)
            investments = sorted(self.investments_repo.find_by_ticker(ticker), key=lambda i: i.subject)
            for subject, investments in groupby(investments, key=lambda i: i.subject):
                logger.info(f'handling {subject}')
                self._handle_events(subject, ticker, [event], list(investments))

    def check_for_applicable_corporate_events(self, subject, investments):
        investments = filter(
            lambda i: i.operation in [OperationType.BUY, OperationType.SELL] and not i.alias_ticker,
            investments)
        investments_map = groupby(sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker)

        for ticker, investments in investments_map:
            investments = list(investments)
            oldest = min([i.date for i in investments])
            isin_code = self.ticker_info.isin_code_from_ticker(ticker)
            events = self.repo.corporate_events_from(isin_code, oldest)

            if events:
                all_ticker_investments = self.investments_repo.find_by_subject_and_ticker(subject, ticker)
                self._handle_events(subject, ticker, events, all_ticker_investments)

    def _handle_events(self, subject, ticker, events, investments):
        for event in events:
            affected_investments = list(
                filter(lambda i, with_date=event.with_date: i.date <= with_date, investments))
            logger.info(f'applicable event: {event}')

            if event.type == 'DESDOBRAMENTO':
                split_inv = self._handle_split_event(subject, event, ticker, affected_investments)
                investments.append(split_inv)
            elif event.type == 'GRUPAMENTO':
                group_inv = self._handle_group_event(subject, event, ticker, affected_investments)
                investments.append(group_inv)
            elif event.type == 'INCORPORACAO':
                incorp_inv = self._handle_incorporation_event(subject, event, ticker, affected_investments)
                investments.append(incorp_inv)
            else:
                logger.warning(f'No implementation for event type of {event.type}')

    def _handle_split_event(self, subject, event, ticker, affected_investments):
        amount = self._affected_investments_amount(affected_investments)
        factor = Decimal(event.grouping_factor / 100)
        _id = self._create_id_from_corp_event(ticker, event)
        split_investment = StockInvestment(amount=amount * factor, price=Decimal(0), ticker=ticker,
                                           operation=OperationType.SPLIT,
                                           date=event.with_date + relativedelta(days=1),
                                           type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)

        self.async_portfolio.send(subject, split_investment)
        return split_investment

    def _handle_group_event(self, subject, event, ticker, affected_investments):
        amount = self._affected_investments_amount(affected_investments)
        _id = self._create_id_from_corp_event(ticker, event)
        factor = event.grouping_factor
        group_investment = StockInvestment(
            amount=amount - Decimal(
                math.ceil((amount * Decimal(factor)).quantize(Decimal('0.01')))),
            price=Decimal(0), ticker=ticker, operation=OperationType.GROUP,
            date=event.with_date + relativedelta(days=1),
            type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)

        self.async_portfolio.send(subject, group_investment)
        return group_investment

    def _handle_incorporation_event(self, subject, event, ticker, affected_investments: List[StockInvestment]):
        new_ticker = self.ticker_info.ticker_from_isin_code(event.emitted_asset)
        amount = self._affected_investments_amount(affected_investments)
        factor = Decimal(event.grouping_factor / 100)
        _id = self._create_id_from_corp_event(ticker, event)

        if factor > 1:
            incorp_investment = StockInvestment(amount=amount * factor, price=Decimal(0), ticker=ticker,
                                                operation=OperationType.INCORP_ADD, alias_ticker=new_ticker,
                                                date=event.with_date + relativedelta(days=1),
                                                type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)
        elif factor < 1:
            incorp_investment = StockInvestment(
                amount=amount - Decimal(
                    math.ceil((amount * Decimal(factor)).quantize(Decimal('0.01')))),
                price=Decimal(0),
                ticker=ticker, operation=OperationType.INCORP_SUB, alias_ticker=new_ticker,
                date=event.with_date + relativedelta(days=1),
                type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)
        else:
            incorp_investment = StockInvestment(
                amount=Decimal(0), price=Decimal(0), alias_ticker=new_ticker,
                ticker=ticker, operation=OperationType.INCORP_ADD,
                date=event.with_date + relativedelta(days=1),
                type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)

        self.async_portfolio.send(subject, incorp_investment)
        for investment in affected_investments:
            investment.alias_ticker = new_ticker
            self.async_portfolio.send(subject, investment)

        return incorp_investment

    @staticmethod
    def _create_id_from_corp_event(ticker, event):
        return f"{ticker}{event.type}{event.deliberate_on.strftime('%Y%m%d')}{event.with_date.strftime('%Y%m%d')}{event.emitted_asset}"

    @staticmethod
    def _affected_investments_amount(affected_investments):
        amount = Decimal(0)
        for inv in affected_investments:
            if inv.operation in [OperationType.BUY, OperationType.SPLIT, OperationType.INCORP_ADD]:
                amount = amount + inv.amount
            else:
                amount = amount - inv.amount
        return amount


if __name__ == '__main__':
    core = CorporateEventsCore()
    # invs = InvestmentRepository().find_by_subject('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    # CorporateEventsCore().check_for_applicable_corporate_events('440b0d96-395d-48bd-aaf2-58dbf7e68274', invs)
    core.handle_today_corporate_events()
    # CorporateEventsCore().process_corporate_events_file(None, None)
    # data = JsonUtils.dump({"cnpj": "0", "identifierFund": "RBRM", "typeFund": 7}).encode('UTF-8')
    # base64_bytes = base64.b64encode(data)
    # base64_message = base64_bytes.decode('ascii')
    # print(base64_message)
    # # eyJjbnBqIjoiMCIsImlkZW50aWZpZXJGdW5kIjoiUkJSTSIsInR5cGVGdW5kIjo3fQ==
