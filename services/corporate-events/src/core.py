import logging
import math
from datetime import datetime
from decimal import Decimal
from io import StringIO
from itertools import groupby
from typing import List

import pandas as pd
from dateutil.relativedelta import relativedelta

from adapters import B3CorporateEventsData, B3CorporateEventsBucket, CorporateEventsRepository, InvestmentRepository, \
    AsyncPortfolioQueue
from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CorporateEventsCore:
    def __init__(self):
        self.b3 = B3CorporateEventsData()
        self.bucket = B3CorporateEventsBucket()
        self.repo = CorporateEventsRepository()
        self.investments_repo = InvestmentRepository()
        self.async_portfolio = AsyncPortfolioQueue()

    def download_today_corporate_events(self):
        today = datetime.now().date()
        companies_data = self.b3.get_updated_corporate_events_link(today)
        for data in companies_data:
            if 'fundsPage' in data.url:
                continue
            tables = pd.read_html(data.url)
            count = 0
            for table in tables:
                csv_name = f'{data.code_cvm}-{today.strftime("%Y%m%d")}-{count}.csv'
                csv_buffer = StringIO()
                table.to_csv(csv_buffer)
                self.bucket.put(csv_buffer, csv_name)
                count = count + 1

    def process_corporate_events_file(self, bucket_name, file_path):
        downloaded_path = self.bucket.download_file(bucket_name, file_path)
        table = pd.read_csv(downloaded_path)

        if set(table.columns) == {'Unnamed: 0', 'Proventos', 'Código ISIN', 'Deliberado em',
                                  'Negócios com até', '% / Fator de Grupamento', 'Ativo Emitido',
                                  'Observações'}:
            table.drop('Unnamed: 0', inplace=True, axis=1)
            table.columns = ['proventos', 'codigo_isin', 'deliberado_em', 'negocios_com_ate',
                             'fator_de_grupamento_perc', 'ativo_emitido', 'observacoes']

            for i, row in table.iterrows():
                sql = f"DELETE FROM b3_corporate_events WHERE codigo_isin = '{row.codigo_isin}' " \
                      f"and proventos = '{row.proventos}' and deliberado_em = '{row.deliberado_em}' " \
                      f"and negocios_com_ate = '{row.negocios_com_ate}' and ativo_emitido = '{row.ativo_emitido}'" \
                      f"and fator_de_grupamento_perc = '{row.fator_de_grupamento_perc}'"
                engine = self.repo.get_engine()
                engine.execute(sql)

            table.to_sql('b3_corporate_events', con=self.repo.get_engine(), if_exists='append', index=False)

        self.bucket.move_file_to_archive(bucket_name, file_path)
        self.bucket.clean_up()

    def check_for_applicable_corporate_events(self, subject, investments):
        investments = filter(
            lambda i: i.operation not in [OperationType.SPLIT, OperationType.GROUP] and not i.alias_ticker,
            investments)
        investments_map = groupby(sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker)

        for ticker, investments in investments_map:
            investments = list(investments)
            oldest = min([i.date for i in investments])
            isin_code = self.repo.get_isin_code_from_ticker(ticker)
            events = self.repo.get_corporate_events(isin_code, oldest)

            if events:
                all_ticker_investments = self.investments_repo.find_by_subject_and_ticker(subject, ticker)

                for event in events:
                    affected_investments = list(
                        filter(lambda i: i.date <= event.negocios_com_ate, all_ticker_investments))

                    if event.proventos == 'DESDOBRAMENTO':
                        split_investment = self._handle_split_event(subject, event, ticker, affected_investments)
                        all_ticker_investments.append(split_investment)
                    elif event.proventos == 'GRUPAMENTO':
                        group_investment = self._handle_group_event(subject, event, ticker, affected_investments)
                        all_ticker_investments.append(group_investment)
                    elif event.proventos == 'INCORPORACAO':
                        self._handle_incorporation_event(subject, event, affected_investments)
                    else:
                        logger.warning(f'No implementation for event type of {event.proventos}')

    def _handle_split_event(self, subject, event, ticker, affected_investments):
        amount = self._affected_investments_amount(affected_investments)
        factor = Decimal(event.fator_de_grupamento_perc / 100)
        _id = self._create_id_from_corp_event(ticker, event)
        split_investment = StockInvestment(amount=amount * factor, price=Decimal(0), ticker=ticker,
                                           operation=OperationType.SPLIT,
                                           date=event.negocios_com_ate + relativedelta(days=1),
                                           type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)

        self.async_portfolio.send(subject, split_investment)

        return split_investment

    def _handle_group_event(self, subject, event, ticker, affected_investments):
        amount = self._affected_investments_amount(affected_investments)
        _id = self._create_id_from_corp_event(ticker, event)
        group_investment = StockInvestment(
            amount=Decimal(amount - Decimal(math.ceil(amount * Decimal(event.fator_de_grupamento_perc)))),
            price=Decimal(0), ticker=ticker, operation=OperationType.GROUP,
            date=event.negocios_com_ate + relativedelta(days=1),
            type=InvestmentsType.STOCK, broker='', subject=subject, id=_id)

        self.async_portfolio.send(subject, group_investment)

        return group_investment

    def _handle_incorporation_event(self, subject, event, affected_investments: List[StockInvestment]):
        new_ticker = self.repo.get_ticker_from_isin_code(event.ativo_emitido)
        for investment in affected_investments:
            investment.alias_ticker = new_ticker
            self.async_portfolio.send(subject, investment)

    @staticmethod
    def _create_id_from_corp_event(ticker, event):
        return f"{ticker}{event.proventos}{event.deliberado_em.strftime('%Y%m%d')}{event.negocios_com_ate.strftime('%Y%m%d')}{event.fator_de_grupamento_perc}"

    @staticmethod
    def _affected_investments_amount(affected_investments):
        amount = Decimal(0)
        for inv in affected_investments:
            if inv.operation == OperationType.BUY:
                amount = amount + inv.amount
            else:
                amount = amount - inv.amount
        return amount


if __name__ == '__main__':
    invs = InvestmentRepository().find_by_subject('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    CorporateEventsCore().check_for_applicable_corporate_events('440b0d96-395d-48bd-aaf2-58dbf7e68274', invs)
    # data = JsonUtils.dump({"cnpj": "0", "identifierFund": "RBRM", "typeFund": 7}).encode('UTF-8')
    # base64_bytes = base64.b64encode(data)
    # base64_message = base64_bytes.decode('ascii')
    # print(base64_message)
    # # eyJjbnBqIjoiMCIsImlkZW50aWZpZXJGdW5kIjoiUkJSTSIsInR5cGVGdW5kIjo3fQ==
