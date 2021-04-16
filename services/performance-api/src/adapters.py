from collections import namedtuple
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import List

import boto3
from boto3.dynamodb.conditions import Key
from sqlalchemy import create_engine
from yahooquery import Ticker

from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils, JsonUtils
from models import Portfolio

# logging.basicConfig(level=logging.DEBUG)

IntraDayData = namedtuple('IntraDayData', 'price prev_close_price change name')
MonthData = namedtuple('MonthlyData', 'date open close change')


class MarketData:
    def __init__(self):
        _secrets_client = boto3.client("secretsmanager")
        secret = JsonUtils.load(_secrets_client.get_secret_value(
            SecretId='rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres')['SecretString'])
        self._username = secret['username']
        self._password = secret['password']
        self._port = secret['port']
        self._host = secret['host']

        self.yahoo_ticker = None
        self._engine = None

    def get_engine(self):
        if self._engine is None:
            self._engine = create_engine(
                f'postgresql://{self._username}:{self._password}@{self._host}:{self._port}/marketdata')
        return self._engine

    def ticker_intraday_date(self, ticker: str):
        if self.yahoo_ticker is None:
            self.yahoo_ticker = Ticker(f'{ticker}.SA')
        else:
            self.yahoo_ticker.symbols = f'{ticker}.SA'
        result = self.yahoo_ticker.price[f'{ticker}.SA']
        return IntraDayData(Decimal(result['regularMarketPrice']).quantize(Decimal('0.01')),
                            Decimal(result['regularMarketPreviousClose']).quantize(Decimal('0.01')),
                            Decimal((result['regularMarketChangePercent']) * 100).quantize(Decimal('0.01')),
                            result['shortName'])

    def ibov_from_date(self, date_from, conn=None):
        if not conn:
            conn = self.get_engine()
        sql = f"SELECT candle_date, open_price, close_price from b3_monthly_chart where ticker = 'IBOVESPA' and candle_date >= '{date_from.strftime('%Y-%m-01')}'order by candle_date"
        result = conn.execute(sql)

        series = []
        for row in result:
            candle_date = row[0]
            open_price = row[1]
            close_price = row[2]
            series.append(MonthData(candle_date, open_price, close_price, 0))

        return series

    def ticker_month_data(self, ticker, _date, alias_ticker='', conn=None):
        """
            Gets candle(open, close) for the entire date.year/date.month
        """
        if not conn:
            conn = self.get_engine()
        date_from = date(_date.year, _date.month, 1)

        if alias_ticker:
            sql = f"SELECT candle_date, open_price, close_price, ticker from b3_monthly_chart where ticker in ('{ticker}', '{alias_ticker}') and candle_date = '{date_from.strftime('%Y-%m-%d')}'"
        else:
            sql = f"SELECT candle_date, open_price, close_price, ticker from b3_monthly_chart where ticker = '{ticker}' and candle_date = '{date_from.strftime('%Y-%m-%d')}'"

        result = conn.execute(sql)

        open_price = Decimal(0)
        close_price = Decimal(0)

        for row in result:
            if result.rowcount == 2:
                if row[3] == ticker:
                    open_price = row[1]
                else:
                    close_price = row[2]
            else:
                open_price = row[1]
                close_price = row[2]

        if ticker == 'TIET11':
            # TODO REMOVE THIS IF
            print(ticker, MonthData(date_from, open_price, close_price, 0))
        return MonthData(date_from, open_price, close_price, 0)


class InvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource('dynamodb').Table('Investments')

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject))
        print(f'RESULT: {result}')
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))

    def batch_save(self, investments: [Investment]):
        with self.__investments_table.batch_writer() as batch:
            for investment in investments:
                batch.put_item(Item=investment.to_dict())


class PortfolioRepository:
    def __init__(self):
        self._portfolio_table = boto3.resource('dynamodb').Table('Portfolio')

    def find(self, subject) -> Portfolio:
        result = self._portfolio_table.query(KeyConditionExpression=Key('subject').eq(subject))
        if result['Items']:
            return Portfolio(**result['Items'][0])
        print(f"No Portfolio yet for subject: {subject}")

    def save(self, portfolio: Portfolio):
        print(f'Saving portfolio: {asdict(portfolio)}')
        self._portfolio_table.put_item(Item=portfolio.to_dict())
