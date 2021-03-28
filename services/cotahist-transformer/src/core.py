from decimal import Decimal
from itertools import groupby

from adapters import B3CotaHistBucket
from auroradata.aurora import AuroraData
from models import B3DailySeries, BDICodes


class CotaHistTransformerCore:
    def __init__(self):
        secret = "arn:aws:secretsmanager:us-east-2:831967415635:secret:rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres-z9xJqf"
        cluster = "arn:aws:rds:us-east-2:831967415635:cluster:serverless-goatfolio-dev-marketdatardscluster-dq6ryzdhjru0"
        database = "marketdata"
        self.aurora_data = AuroraData(cluster, secret, database)
        self.bucket = B3CotaHistBucket()

    def transform_cota_hist(self):
        # dowloaded_path = self.bucket.download(file)
        downloaded_path = 'COTAHIST_M022021.TXT'
        series = []
        with open(downloaded_path, 'r') as fp:
            for line in fp:
                if line.startswith('99COTAHIST') or line.startswith('00COTAHIST'):
                    continue
                data = B3DailySeries(line)
                if data.codigo_bdi not in [BDICodes.STOCK, BDICodes.FII, BDICodes.ETF]:
                    continue
                series.append(data)

        print(self.persist_monthly_series(series))

    def persist_monthly_series(self, series):
        grouped_by_ticker = groupby(sorted(series, key=lambda e: e.codigo_negociacao),
                                    key=lambda e: e.codigo_negociacao)
        sql = 'INSERT INTO b3_monthly_chart (ticker, candle_date, company_name, open_price, close_price, average_price, max_price, min_price, volume) values (:ticker, :candle_date, :company_name, :open_price, :close_price, :average_price, :max_price, :min_price, :volume)'
        sql_parameter_sets = []
        for ticker, investments in grouped_by_ticker:
            investments = list(sorted(investments, key=lambda i: i.data_pregao))
            company_name = investments[0].nome_resumido_empresa_emissora
            open_price = investments[0].preco_abertura
            close_price = investments[-1].preco_ultimo
            max_price = max([i.preco_maximo for i in investments])
            min_price = min([i.preco_minimo for i in investments])
            average_price = (sum([i.preco_medio for i in investments]) / len(investments)).quantize(Decimal('0.01'))
            volume = sum([i.numero_de_negocios for i in investments])
            date = investments[0].data_pregao[:7] + '-01'

            entry = [
                {'name': 'ticker', 'value': {'stringValue': ticker}},
                {'name': 'candle_date', 'typeHint': 'DATE', 'value': {'stringValue': f"{date}"}},
                {'name': 'company_name', 'value': {'stringValue': company_name}},
                {'name': 'open_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{open_price}'}},
                {'name': 'close_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{close_price}'}},
                {'name': 'average_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{average_price}'}},
                {'name': 'max_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{max_price}'}},
                {'name': 'min_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{min_price}'}},
                {'name': 'volume', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{volume}'}},
            ]
            sql_parameter_sets.append(entry)
        self._persist_in_aurora(sql, sql_parameter_sets)

    def persist_daily_series(self, series):
        sql = 'INSERT INTO b3_daily_chart (ticker, candle_date, company_name, open_price, close_price, average_price, max_price, min_price, volume) values (:ticker, :candle_date, :company_name, :open_price, :close_price, :average_price, :max_price, :min_price, :volume)'
        sql_parameter_sets = []
        for element in series:
            entry = [
                {'name': 'ticker', 'value': {'stringValue': element.codigo_negociacao}},
                {'name': 'candle_date', 'typeHint': 'DATE', 'value': {'stringValue': f"{element.data_pregao}"}},
                {'name': 'company_name', 'value': {'stringValue': element.nome_resumido_empresa_emissora}},
                {'name': 'open_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{element.preco_abertura}'}},
                {'name': 'close_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{element.preco_ultimo}'}},
                {'name': 'average_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{element.preco_medio}'}},
                {'name': 'max_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{element.preco_maximo}'}},
                {'name': 'min_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{element.preco_minimo}'}},
                {'name': 'volume', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{element.numero_de_negocios}'}},
            ]
            sql_parameter_sets.append(entry)
        self._persist_in_aurora(sql, sql_parameter_sets)

    def _persist_in_aurora(self, sql, sql_parameter_sets):
        print(f'Entrys: {len(sql_parameter_sets)}')
        position = 0
        while position < len(sql_parameter_sets):
            print(self.aurora_data.batch_execute_statement(sql=sql,
                                                           parameter_sets=sql_parameter_sets[position:position + 1000]))
            position = position + 1000


if __name__ == '__main__':
    CotaHistTransformerCore().transform_cota_hist()
