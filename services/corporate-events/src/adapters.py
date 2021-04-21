import logging
import os
import re
from dataclasses import asdict
from io import StringIO
from typing import List

import boto3 as boto3
import requests
from boto3.dynamodb.conditions import Key, Attr

from goatcommons.constants import InvestmentsType
from goatcommons.models import Investment, StockInvestment
from goatcommons.utils import InvestmentUtils, JsonUtils
from model import CompanyCorporateEventsData, EarningsInAssetCorporateEvent, AsyncInvestmentAddRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource('dynamodb').Table('Investments')

    def find_by_subject_and_ticker(self, subject, ticker):
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject),
                                                FilterExpression=Attr("ticker").eq(ticker))
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject))
        print(f'RESULT: {result}')
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))


class B3CorporateEventsData:
    URL = 'https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0='
    DATE_FORMAT = '%d/%m/%Y'
    ALTERNATIVE_DATE_FORMAT = '%m/%d/%Y'  # for some reason sometimes de API return day/month/year and other times month/day/year

    def get_updated_corporate_events_link(self, date) -> List[CompanyCorporateEventsData]:
        data = requests.get(self.URL, verify=False).json()
        logger.info(f'b3 corporate events response: {data}')
        filtered_data = list(filter(lambda i: i['date'] == date.strftime(self.DATE_FORMAT), data))
        if not filtered_data:
            logger.info('trying alternative date format')
            filtered_data = list(
                filter(lambda i: i['date'] == date.strftime(self.ALTERNATIVE_DATE_FORMAT), data))

        if not filtered_data:
            logger.info(f'No corporate events for {date.strftime(self.DATE_FORMAT)}')
            return []
        return list(map(
            lambda i: CompanyCorporateEventsData(company_name=i['companyName'], trading_name=i['tradingName'],
                                                 code=i['code'],
                                                 segment=i['segment'], code_cvm=i['codeCvm'],
                                                 url=re.sub(r'en-US$', 'pt-BR', i['url'])),
            filtered_data[0]['results']))


class B3CorporateEventsBucket:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self._downloaded_files = []
        self.bucket_name = os.getenv('CORPORATE_BUCKET')

    def download_file(self, bucket, file_path):
        destination = f"/tmp/{file_path.split('/')[-1]}"
        logger.info(f'Downloading to: {destination}')
        self.s3.download_file(bucket, file_path, destination)
        logger.info(f'Download finish')
        self._downloaded_files.append(destination)
        return destination

    def put(self, buffer: StringIO, file_name):
        self.s3.put_object(Body=buffer.getvalue(), Bucket=self.bucket_name, Key=f'new/{file_name}')

    def move_file_to_archive(self, bucket, file_path):
        self.s3.copy_object(Bucket=bucket, CopySource=f'{bucket}/{file_path}', Key=f"archive/{file_path}")
        self.s3.delete_object(Bucket=bucket, Key=file_path)

    def clean_up(self):
        for file in self._downloaded_files:
            os.system(f'rm -f {file}')


class CorporateEventsRepository:
    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('CorporateEvents')

    def corporate_events_from(self, isin_code, date):
        result = self.__table.query(IndexName='isinDateGlobalIndex',
                                    KeyConditionExpression=Key('isin_code').eq(isin_code) & Key('with_date').lte(
                                        date.strftime('%Y%m%d')))
        return list(map(lambda i: EarningsInAssetCorporateEvent(**i), result['Items']))

    def batch_save(self, records):
        with self.__table.batch_writer() as batch:
            for record in records:
                batch.put_item(Item=record.to_dict())


class TickerInfoRepository:
    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('TickerInfo')

    def isin_code_from_ticker(self, ticker):
        result = self.__table.query(KeyConditionExpression=Key('ticker').eq(ticker))
        if result['Items']:
            return result['Items'][0]['isin']

    def ticker_from_isin_code(self, isin_code):
        result = self.__table.query(IndexName='isinGlobalIndex', KeyConditionExpression=Key('isin').eq(isin_code))
        if result['Items']:
            return result['Items'][0]['ticker']


class AsyncPortfolioQueue:
    QUEUE_NAME = 'AddInvestmentQueue'

    def __init__(self):
        self._queue = boto3.resource('sqs').get_queue_by_name(QueueName=self.QUEUE_NAME)

    def send(self, subject, investment: StockInvestment):
        request = AsyncInvestmentAddRequest(subject, InvestmentsType.STOCK, investment.to_dict())
        self._queue.send_message(MessageBody=JsonUtils.dump(asdict(request)))
