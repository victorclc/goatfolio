import logging
import os
import zipfile
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import List

import boto3 as boto3
import requests

from goatcommons.cedro.client import CedroMarketDataClient
from models import B3CotaHistData

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class B3CotaHistBucket:
    BUCKET_NAME = f"{os.getenv('STAGE')}-b3cotahist"

    def __init__(self):
        self.s3 = boto3.client('s3')
        self._downloaded_files = []

    def download_file(self, bucket, file_path):
        destination = f"/tmp/{file_path.split('/')[-1]}"
        logger.info(f'Downloading to: {destination}')
        self.s3.download_file(bucket, file_path, destination)
        logger.info(f'Download finish')
        self._downloaded_files.append(destination)
        return destination

    def move_file_to_archive(self, bucket, file_path):
        self.s3.copy_object(Bucket=bucket, CopySource=f'{bucket}/{file_path}', Key=f"archive/{file_path}")
        self.s3.delete_object(Bucket=bucket, Key=file_path)

    def put(self, buffer: BytesIO, file_name):
        self.s3.put_object(Body=buffer.getvalue(), Bucket=self.BUCKET_NAME, Key=f'monthly/{file_name}')

    def clean_up(self):
        for file in self._downloaded_files:
            os.system(f'rm -f {file}')


class CotaHistRepository:
    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('MarketData')

    def save(self, data: B3CotaHistData):
        self.__table.put_item(Item=data.to_dict())

    def batch_save(self, series: List[B3CotaHistData]):
        with self.__table.batch_writer() as batch:
            for data in series:
                batch.put_item(Item=data.to_dict())


class TickerInfoRepository:
    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('TickerInfo')

    def save(self, info: dict):
        self.__table.put_item(Item=info)

    def batch_save(self, infos: List[dict]):
        with self.__table.batch_writer() as batch:
            for info in infos:
                batch.put_item(Item=info)


class IBOVFetcher:
    def __init__(self):
        self.client = CedroMarketDataClient()

    def fetch_last_month_data(self):
        response = self.client.quote('IBOV')
        close = response['lastTrade']
        date = datetime.now()
        data = B3CotaHistData()

        data.load_ibov('IBOVESPA', date.strftime('%Y%m01'), 'Indice Ibovespa',
                       Decimal(0).quantize(Decimal('0.01')),
                       Decimal(close).quantize(Decimal('0.01')),
                       Decimal(0).quantize(Decimal('0.01')),
                       Decimal(0).quantize(Decimal('0.01')),
                       Decimal(0).quantize(Decimal('0.01')))
        return data


class CotaHistDownloader:
    BASE_URL = 'https://bvmf.bmfbovespa.com.br/InstDados/SerHist/{0}'
    TEMP_DIR = '.'

    def download_monthly_file(self, year, month):
        base_file_name = f"COTAHIST_M{month:02}{year}"
        response = requests.get(self.BASE_URL.format(f'{base_file_name}.ZIP'), verify=False)

        with zipfile.ZipFile(BytesIO(response.content), 'r') as zip_file:
            return zip_file.read(f'{base_file_name}.TXT')
