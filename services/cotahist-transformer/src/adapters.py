import logging
import os
from typing import List

import boto3 as boto3

from goatcommons.utils import JsonUtils
from models import B3CotaHistData
from pandas import DataFrame
from sqlalchemy import create_engine

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
        _secrets_client = boto3.client("secretsmanager")
        # TODO put secret id on env variaable
        secret = JsonUtils.load(_secrets_client.get_secret_value(
            SecretId='rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres')['SecretString'])

        self._username = secret['username']
        self._password = secret['password']
        self._port = secret['port']
        self._host = secret['host']

        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            logger.info('Creating engine')
            self._engine = create_engine(
                f'postgresql://{self._username}:{self._password}@{self._host}:{self._port}/marketdata')
            logger.info('Engine created')
        return self._engine

    def save(self, series: List[B3CotaHistData]):
        dataframe = DataFrame([s.row for s in series], columns=B3CotaHistData.columns_names())
        logger.info('Saving to database')
        dataframe.to_sql('b3_monthly_chart', con=self._get_engine(), if_exists='append', index=False)
        logger.info('Saved on database')
