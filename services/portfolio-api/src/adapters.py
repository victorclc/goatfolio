import logging
from typing import List

import boto3
from boto3.dynamodb.conditions import Key

from goatcommons.models import Investment
from goatcommons.portfolio.models import Portfolio, StockConsolidated
from goatcommons.utils import InvestmentUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource('dynamodb').Table('Investments')

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject))
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))

    def find_by_subject_and_date(self, subject, operand, value) -> List[Investment]:
        # TODO tratar operand
        result = self.__investments_table.query(IndexName='subjectDateGlobalIndex',
                                                KeyConditionExpression=Key('subject').eq(subject) & Key('date').gte(
                                                    value))
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))

    def save(self, investment: Investment):
        self.__investments_table.put_item(Item=investment.to_dict())

    def delete(self, investment_id, subject):
        self.__investments_table.delete_item(Key={'subject': subject, 'id': investment_id})

    def batch_save(self, investments: [Investment]):
        with self.__investments_table.batch_writer() as batch:
            for investment in investments:
                batch.put_item(Item=investment.to_dict())


class PortfolioRepository:
    def __init__(self):
        self._portfolio_table = boto3.resource('dynamodb').Table('Portfolio')

    def find(self, subject) -> Portfolio:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key('subject').eq(subject) & Key('ticker').eq(subject))
        if result['Items']:
            return Portfolio(**result['Items'][0])
        logger.info(f"No Portfolio yet for subject: {subject}")

    def find_ticker(self, subject, ticker) -> StockConsolidated:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key('subject').eq(subject) & Key('ticker').eq(ticker))
        if result['Items']:
            return StockConsolidated(**result['Items'][0])
        logger.info(f"No {ticker} yet for subject: {subject}")

    def find_alias_ticker(self, subject, ticker) -> StockConsolidated:
        result = self._portfolio_table.query(IndexName='subjectAliasTickerGlobalIndex',
                                             KeyConditionExpression=Key('subject').eq(subject) & Key('alias_ticker').eq(
                                                 ticker))
        if result['Items']:
            return StockConsolidated(**result['Items'][0])
        logger.info(f"No alias {ticker} yet for subject: {subject}")

    def save(self, obj):
        logger.info(f'Saving: {obj.to_dict()}')
        self._portfolio_table.put_item(Item=obj.to_dict())
