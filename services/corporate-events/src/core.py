import logging
from datetime import datetime
from itertools import groupby

import pandas as pd

from adapters import B3CorporateEventsData, B3CorporateEventsBucket, CorporateEventsRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CorporateEventsCore:
    def __init__(self):
        self.b3 = B3CorporateEventsData()
        self.bucket = B3CorporateEventsBucket()
        self.repo = CorporateEventsRepository()

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
                table.to_csv(f's3://dev-b3-corporate-events/new/{csv_name}')  # TODO GET BUCKET NAME FROM ENV VARIABLE
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

    def check_corporate_events(self, subject, investments):
        # TODO  validar se investimento adicionado eh do tipo SPLIT ou GROUP ou qualquer outra coisa desse servico

        investments_map = groupby(sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker)

        for ticker, investments in investments_map:
            print(ticker)
            investments = list(investments)
            oldest = min([i.date for i in investments])
            newer = max([i.date for i in investments])
            print(oldest)
            print(newer)
        # agrupar por ticker
        # pegar maior e menor data de investimento do ticker
        # fazer query na b3_corporate_eventes
        # se retornou algo
        # buscar investimentos na tabela Investment
        # calcular valor do split ou group
        # adicionar na tabela investimentos de um jeito que identifica q eh um split ou group


if __name__ == '__main__':
    # invs = InvestmentRepository().find_by_subject('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    CorporateEventsCore().download_today_corporate_events()
    # data = JsonUtils.dump({"cnpj": "0", "identifierFund": "RBRM", "typeFund": 7}).encode('UTF-8')
    # base64_bytes = base64.b64encode(data)
    # base64_message = base64_bytes.decode('ascii')
    # print(base64_message)
    # # eyJjbnBqIjoiMCIsImlkZW50aWZpZXJGdW5kIjoiUkJSTSIsInR5cGVGdW5kIjo3fQ==
