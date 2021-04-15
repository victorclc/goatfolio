import logging
import os
import re
from typing import List

import boto3 as boto3
import requests
from boto3.dynamodb.conditions import Key
from sqlalchemy import create_engine

from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils, JsonUtils
from model import CorporateEventData

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource('dynamodb').Table('Investments')

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject))
        print(f'RESULT: {result}')
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))


class B3CorporateEventsData:
    URL = 'https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0='
    DATE_FORMAT = '13/%m/%Y'

    def get_updated_corporate_events_link(self, date) -> List[CorporateEventData]:
        data = requests.get(self.URL, verify=False).json()
        logger.info(f'b3 corporate events response: {data}')
        filtered_data = list(filter(lambda i: i['date'] == date.strftime(self.DATE_FORMAT), data))

        if not filtered_data:
            logger.info(f'No corporate events for {date.strftime(self.DATE_FORMAT)}')
            return []
        return list(map(
            lambda i: CorporateEventData(company_name=i['companyName'], trading_name=i['tradingName'], code=i['code'],
                                         segment=i['segment'], code_cvm=i['codeCvm'],
                                         url=re.sub(r'en-US$', 'pt-BR', i['url'])),
            filtered_data[0]['results']))


class B3CorporateEventsBucket:
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


class CorporateEventsRepository:
    def __init__(self):
        _secrets_client = boto3.client("secretsmanager")
        logger.info('loading secret')
        secret = JsonUtils.load(_secrets_client.get_secret_value(
            SecretId='rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres')['SecretString'])
        self._username = secret['username']
        self._password = secret['password']
        self._port = secret['port']
        self._host = secret['host']

        self._engine = None

    def get_engine(self):
        if self._engine is None:
            logger.info('Creating engine')
            self._engine = create_engine(
                f'postgresql://{self._username}:{self._password}@{self._host}:{self._port}/marketdata')
            logger.info('Engine created')
        return self._engine
