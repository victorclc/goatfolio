import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import List

import boto3 as boto3
import requests
from dateutil.relativedelta import relativedelta

from models import B3CotaHistData

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class B3CotaHistBucket:
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
    @staticmethod
    def fetch_last_month_data():
        response = \
            requests.get('https://query1.finance.yahoo.com/v7/finance/chart/^BVSP?range=3mo&interval=1mo').json()[
                'chart'][
                'result'][0]

        quote = response['indicators']['quote'][0]
        timestamp = response['timestamp'][2]

        date = datetime.fromtimestamp(timestamp)
        if date.day != 1:
            date = datetime(date.year, date.month, 1) + relativedelta(months=1)

        high = max(quote['high'][2], quote['high'][3])
        low = min(quote['low'][2], quote['low'][3])

        data = B3CotaHistData()
        data.load_ibov('IBOVESPA', date.strftime('%Y%m%d'), 'Indice Ibovespa',
                       Decimal(quote['open'][2]).quantize(Decimal('0.01')),
                       Decimal(quote['close'][3]).quantize(Decimal('0.01')),
                       Decimal(high).quantize(Decimal('0.01')),
                       Decimal(low).quantize(Decimal('0.01')),
                       Decimal(quote['volume'][2]).quantize(Decimal('0.01')))
        return data
