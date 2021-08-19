import logging
import os
from collections import namedtuple
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from functools import wraps
from typing import List

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from dateutil.relativedelta import relativedelta
from redis import Redis

from goatcommons.cedro.client import CedroMarketDataClient
from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils
from models import Portfolio, CandleData

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

IntraDayData = namedtuple('IntraDayData', 'price prev_close_price change name')
MonthData = namedtuple('MonthlyData', 'open close')

redis = Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0)


# TODO: UNIT TEST THIS STUFF
def is_market_open(now):
    return now.weekday() < 5 and 12 <= now.hour <= 21


def next_market_opening(now):
    next_day = now + relativedelta(days=1)
    while next_day.weekday() > 4:
        next_day = next_day + relativedelta(days=1)
    return next_day.replace(hour=12, minute=0, second=0)


def calculate_expiration_time():
    now = datetime.now(tz=timezone.utc)
    if is_market_open(now):
        return 300
    next_opening = next_market_opening(now)
    return int(next_opening.timestamp() - now.timestamp())


def cached_tuple(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key_parts = [func.__name__] + list(args[1:])
        key = '-'.join(key_parts)
        result = None

        try:
            result = redis.get(key)
        except Exception as e:
            logger.exception('CAUGHT EXCEPTION getting key from redis: ', e)

        if result is None:
            value = func(*args, **kwargs)
            try:
                redis.setex(key, calculate_expiration_time(), str(value))
            except Exception as e:
                logger.exception('CAUGHT EXCEPTION putting key from redis: ', e)
        else:
            logger.info(f'{key} in cache, returning.')
            value = eval(result)
        return value

    return wrapper


class MarketData:
    def __init__(self):
        self.repo = MarketDataRepository()
        self.cedro = CedroMarketDataClient()

    @cached_tuple
    def ticker_intraday_date(self, ticker: str):
        result = self.cedro.quote(ticker)
        return IntraDayData(Decimal(result['lastTrade']).quantize(Decimal('0.01')),
                            Decimal(result['previous']).quantize(Decimal('0.01')),
                            Decimal((result['change'])).quantize(Decimal('0.01')),
                            result['company'])

    def ibov_from_date(self, date_from) -> List[CandleData]:
        return self.repo.find_by_ticker_from_date('IBOVESPA', date_from)

    def ticker_monthly_data_from(self, ticker, date_from, alias_ticker=''):
        ticker_candles = self.repo.find_by_ticker_from_date(ticker, date_from)

        if alias_ticker:
            alias_candles = self.repo.find_by_ticker_from_date(alias_ticker, date_from)
            for candle in alias_candles:
                ticker_candle = next((ticker_candle for ticker_candle in ticker_candles if
                                      ticker_candle.candle_date == candle.candle_date), {})
                if ticker_candle:
                    ticker_candle.close_price = candle.close_price
                else:
                    ticker_candles.append(candle)

        response_map = {}
        for candle in ticker_candles:
            response_map[candle.candle_date.strftime('%Y%m01')] = MonthData(candle.open_price, candle.close_price)

        return response_map

    def ticker_month_data(self, ticker, _date, alias_ticker=''):
        """
            Gets candle(open, close) for the entire date.year/date.month
        """
        open_price = Decimal(0)
        close_price = Decimal(0)
        if alias_ticker:
            candles = self.repo.batch_get_by_tickers_and_date([ticker, alias_ticker], _date)
            if candles:
                if len(candles) == 2:
                    for candle in candles:
                        if candle.ticker == ticker:
                            open_price = candle.open_price
                        else:
                            close_price = candle.close_price
                else:
                    open_price = candles[0].open_price
                    close_price = candles[0].close_price
        else:
            candle = self.repo.find_by_ticker_and_date(ticker, _date)
            if candle:
                open_price = candle.open_price
                close_price = candle.close_price

        return MonthData(open_price, close_price)


class MarketDataRepository:
    DATE_FORMAT = '%Y%m01'

    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('MarketData')
        self.__client = boto3.client('dynamodb')
        self.__deserializer = TypeDeserializer()

    def find_by_ticker_and_date(self, ticker, _date):
        result = self.__table.query(
            KeyConditionExpression=Key('ticker').eq(ticker) & Key('candle_date').eq(_date.strftime(self.DATE_FORMAT)))
        if result['Items']:
            return CandleData(**result['Items'][0])

    def find_by_ticker_from_date(self, ticker, _date):
        result = self.__table.query(
            KeyConditionExpression=Key('ticker').eq(ticker) & Key('candle_date').gte(_date.strftime(self.DATE_FORMAT)))
        if result['Items']:
            return [CandleData(**data) for data in result['Items']]
        return []

    def batch_get_by_tickers_and_date(self, tickers, _date):
        response = self.__client.batch_get_item(
            RequestItems={
                'MarketData': {
                    'Keys': [{'ticker': {'S': ticker}, 'candle_date': {'S': _date.strftime(self.DATE_FORMAT)}} for
                             ticker in tickers],
                    'ConsistentRead': False
                }
            },
            ReturnConsumedCapacity='NONE'
        )
        candles = []
        for data in response['Responses']['MarketData']:
            candles.append(CandleData(**self.__deserializer.deserialize({'M': data})))
        return candles


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


if __name__ == '__main__':
    start = datetime.now().timestamp()
    cedro = CedroMarketDataClient()
    cedro.quotes(['bidi11', 'ifix', 'sqia3', 'ibov', 'mglu3', 'wege3', 'ninj3'])
    end = datetime.now().timestamp()
    print(f"TOOKED: {end - start} seconds")

# if __name__ == '__main__':
# r = Redis(host='localhost', port=6379, db=0)
# data = MarketData().ticker_intraday_date('BIDI11')
# print(data)
# print(isinstance(data, tuple))
# # print(r.get('BIDI11'))
# # # r.set('BIDI11', str(Decimal('231.05')))
# # r.setex('BIDI11', 43200, str(data))
# # print(eval(r.get('BIDI11')))
