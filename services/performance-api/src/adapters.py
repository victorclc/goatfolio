from collections import namedtuple
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import List

import boto3
from boto3.dynamodb.conditions import Key
from yahooquery import Ticker

from auroradata.aurora import AuroraData
from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils
from models import Portfolio

# logging.basicConfig(level=logging.DEBUG)

IntraDayData = namedtuple('IntraDayData', 'price prev_close_price change name')
MonthData = namedtuple('MonthlyData', 'date open close change')


class MarketData:
    def __init__(self):
        self.yahoo_ticker = None
        self.history_cache = {}
        secret = "arn:aws:secretsmanager:us-east-2:831967415635:secret:rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres-z9xJqf"
        cluster = "arn:aws:rds:us-east-2:831967415635:cluster:serverless-goatfolio-dev-marketdatardscluster-dq6ryzdhjru0"
        database = "marketdata"
        self.aurora_data = AuroraData(cluster, secret, database)

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

    def ticker_monthly_data(self, ticker, date_from=None):
        if ticker in self.history_cache:
            return self.history_cache[ticker]

        sql = f'SELECT candle_date, open_price, close_price from b3_monthly_chart where ticker = \'{ticker}\' order by candle_date'
        query_response = self.aurora_data.execute_statement(sql)
        result = list()
        for record in query_response['records']:
            candle_date = date.fromisoformat(record[0]['stringValue'])
            open_price = Decimal(record[1]['stringValue'])
            close_price = Decimal(record[2]['stringValue'])
            result.append(MonthData(candle_date, open_price, close_price, 0))
        print(result)
        self.history_cache[ticker] = result

        return result

    def ibov_from_date(self, date_from):
        sql = f"SELECT candle_date, open_price, close_price from b3_monthly_chart where ticker = 'IBOVESPA' and candle_date >= '{date_from.strftime('%Y-%m-%d')}'order by candle_date"
        query_response = self.aurora_data.execute_statement(sql)
        result = list()
        for record in query_response['records']:
            candle_date = date.fromisoformat(record[0]['stringValue'])
            open_price = Decimal(record[1]['stringValue'])
            close_price = Decimal(record[2]['stringValue'])
            result.append(MonthData(candle_date, open_price, close_price, 0))
        print(result)

        return result

    def ticker_month_data(self, ticker, _date):
        """
            Gets candle(open, close) for the entire date.year/date.month
        """
        data = self.ticker_monthly_data(ticker)
        date_from = date(_date.year, _date.month, 1)

        return list(filter(lambda m: m.date == date_from, data))[0]


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
