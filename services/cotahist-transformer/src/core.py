import logging
from datetime import datetime
from decimal import Decimal
from itertools import groupby

from adapters import B3CotaHistBucket, CotaHistRepository
from models import B3CotaHistData, BDICodes

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CotaHistTransformerCore:
    def __init__(self):
        logger.info('Importing bucket')
        self.bucket = B3CotaHistBucket()
        logger.info('Importing repo')
        self.repo = CotaHistRepository()
        logger.info('Imported')

    def transform_cota_hist(self, bucket_name, file_path):
        daily_series = self._load_series_from_file(bucket_name, file_path)
        monthly_series = []
        for ticker, all_investments in groupby(sorted(daily_series, key=lambda e: e.codigo_negociacao),
                                               key=lambda e: e.codigo_negociacao):
            all_investments = list(sorted(all_investments, key=lambda i: i.data_pregao))
            for year_month, investments in groupby(sorted(all_investments, key=lambda i: f'{i.data_pregao[:7]}'),
                                                   key=lambda i: f'{i.data_pregao[:7]}'):
                investments = list(sorted(investments, key=lambda i: i.data_pregao))
                company_name = investments[0].nome_resumido_empresa_emissora
                open_price = investments[0].preco_abertura
                close_price = investments[-1].preco_ultimo
                max_price = max([i.preco_maximo for i in investments])
                min_price = min([i.preco_minimo for i in investments])
                average_price = (sum([i.preco_medio for i in investments]) / len(investments)).quantize(Decimal('0.01'))
                volume = sum([i.numero_de_negocios for i in investments])
                date = datetime.strptime(investments[0].data_pregao[:7] + '-01', '%Y-%m-%d').date()
                isin_code = investments[0].codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel

                data = B3CotaHistData()
                data.load_essentials(ticker, date, company_name, open_price, close_price, average_price, max_price,
                                     min_price, None, None, volume, isin_code)
                monthly_series.append(data)

        print(monthly_series)
        # self.repo.save(monthly_series)
        # self.bucket.move_file_to_archive(bucket_name, file_path)
        # self.bucket.clean_up()

    def _load_series_from_file(self, bucket_name, file_path):
        # downloaded_path = self.bucket.download_file(bucket_name, file_path)
        downloaded_path = 'C:\\Users\\victorclc\\Downloads\\COTAHIST_A2012.txt'
        series = []
        with open(downloaded_path, 'r') as fp:
            logger.info(f'Reading file: {downloaded_path}')
            for line in fp:
                if line.startswith('99COTAHIST') or line.startswith('00COTAHIST'):
                    continue
                data = B3CotaHistData()
                data.load_line(line)
                if data.codigo_bdi not in [BDICodes.STOCK, BDICodes.FII, BDICodes.ETF]:
                    continue
                series.append(data)
        logger.info(f'Finish reading.')
        return series


if __name__ == '__main__':
    core = CotaHistTransformerCore()
    core.transform_cota_hist(None, None)