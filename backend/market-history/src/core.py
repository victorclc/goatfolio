import logging
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from itertools import groupby

from dateutil.relativedelta import relativedelta

from adapters import (
    B3CotaHistBucket,
    CotaHistRepository,
    TickerInfoRepository,
    IBOVFetcher,
    CotaHistDownloader,
)
from models import B3CotaHistData, BDICodes

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CotaHistTransformerCore:
    def __init__(self):
        self.bucket = B3CotaHistBucket()
        self.repo = CotaHistRepository()
        self.info_repo = TickerInfoRepository()

    def get_asset_type(self, codigo_bdi, especificacao: str) -> str:
        if codigo_bdi == "12":
            return "FII"
        if especificacao.startswith("DR"):
            return "BDR"
        return "STOCK"

    def transform_cota_hist(self, bucket_name, file_path):
        daily_series = self._load_series_from_file(bucket_name, file_path)
        monthly_series = []
        infos = {}

        for ticker, all_investments in groupby(
            sorted(daily_series, key=lambda e: e.codigo_negociacao),
            key=lambda e: e.codigo_negociacao,
        ):
            all_investments = list(sorted(all_investments, key=lambda i: i.data_pregao))
            for year_month, investments in groupby(
                sorted(all_investments, key=lambda i: f"{i.data_pregao[:7]}"),
                key=lambda i: f"{i.data_pregao[:7]}",
            ):
                investments = list(sorted(investments, key=lambda i: i.data_pregao))
                company_name = investments[0].nome_resumido_empresa_emissora
                open_price = investments[0].preco_abertura
                close_price = investments[-1].preco_ultimo
                max_price = max([i.preco_maximo for i in investments])
                min_price = min([i.preco_minimo for i in investments])
                average_price = (
                    sum([i.preco_medio for i in investments]) / len(investments)
                ).quantize(Decimal("0.01"))
                volume = sum([i.numero_de_negocios for i in investments])
                date = datetime.strptime(
                    investments[0].data_pregao[:7] + "-01", "%Y-%m-%d"
                ).strftime("%Y%m%d")
                isin_code = investments[
                    0
                ].codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel

                code = ticker[:4]
                _type = self.get_asset_type(investments[0].codigo_bdi, investments[0].especificacao_papel.strip())

                data = B3CotaHistData()
                data.load_essentials(
                    ticker,
                    date,
                    company_name,
                    open_price,
                    close_price,
                    average_price,
                    max_price,
                    min_price,
                    None,
                    None,
                    volume,
                    isin_code,
                )
                monthly_series.append(data)
                if ticker not in infos:
                    infos[ticker] = {
                        "ticker": ticker,
                        "isin": isin_code,
                        "bdi": investments[0].codigo_bdi,
                        "company_name": investments[0].nome_resumido_empresa_emissora,
                        "code": code,
                        "asset_type": _type
                    }

        self.repo.batch_save(monthly_series)
        self.info_repo.batch_save(list(infos.values()))
        self.bucket.move_file_to_archive(bucket_name, file_path)
        self.bucket.clean_up()

    def _load_series_from_file(self, bucket_name, file_path):
        downloaded_path = self.bucket.download_file(bucket_name, file_path)
        series = []
        count = 0

        try:
            with open(downloaded_path, "r") as fp:
                logger.info(f"Reading file: {downloaded_path}")
                for line in fp:
                    count = count + 1
                    if line.startswith("99COTAHIST") or line.startswith("00COTAHIST"):
                        continue
                    data = B3CotaHistData()
                    data.load_line(line)

                    if data.codigo_bdi not in [BDICodes.STOCK, BDICodes.FII, BDICodes.ETF, BDICodes.RECUPERACAO_JUDICIAL]:
                        continue
                    series.append(data)
            logger.info(f"Finish reading.")
        except UnicodeDecodeError as ex:
            logger.info(f"Last processed line: {count}")
            raise ex
        return series

    def update_ibov_history(self):
        fetcher = IBOVFetcher()
        ibov_data = fetcher.fetch_last_month_data()
        self.repo.save(ibov_data)


class CotaHistDownloaderCore:
    def __init__(self):
        self.downloader = CotaHistDownloader()
        self.bucket = B3CotaHistBucket()

    def download_current_monthly_file(self):
        now = datetime.now()
        file_buffer = self.downloader.download_monthly_file(now.year, now.month)
        self.bucket.put(BytesIO(file_buffer), f'M{now.strftime("%Y%m")}.TXT')

    def download_monthly_file(self, year, month):
        file_buffer = self.downloader.download_monthly_file(year, month)
        self.bucket.put(BytesIO(file_buffer), f"M{year}{month:02}.TXT")

