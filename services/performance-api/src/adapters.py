import logging
import os
from collections import namedtuple
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
from goatcommons.portfolio.models import Portfolio, StockConsolidated
from goatcommons.utils import InvestmentUtils
from models import CandleData

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

IntraDayData = namedtuple('IntraDayData', 'price prev_close_price change name')
MonthData = namedtuple('MonthlyData', 'open close')


class RedisMarketData:
    redis = Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0)

    def get_intraday_data(self, key):
        try:
            result = self.redis.get(key.upper())
            if result:
                logger.info(f'{key} in cache, returning.')
                return eval(result)
        except Exception as e:
            logger.exception('CAUGHT EXCEPTION getting key from redis: ', e)

    def put_intraday_data(self, ticker, data):
        try:
            self.redis.setex(ticker.upper(), self.calculate_expiration_time(), str(data))
        except Exception as e:
            logger.exception('CAUGHT EXCEPTION putting key from redis: ', e)

    @staticmethod
    def is_market_open(now):
        return now.weekday() < 5 and 12 <= now.hour <= 21

    @staticmethod
    def next_market_opening(now):
        next_day = now + relativedelta(days=1)
        while next_day.weekday() > 4:
            next_day = next_day + relativedelta(days=1)
        return next_day.replace(hour=12, minute=0, second=0)

    @staticmethod
    def calculate_expiration_time():
        now = datetime.now(tz=timezone.utc)
        if RedisMarketData.is_market_open(now):
            return 300
        next_opening = RedisMarketData.next_market_opening(now)
        return int(next_opening.timestamp() - now.timestamp())

    @staticmethod
    def cached_tuple(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = args[1]
            result = None

            try:
                result = RedisMarketData.redis.get(key)
            except Exception as e:
                logger.exception('CAUGHT EXCEPTION getting key from redis: ', e)

            if result is None:
                value = func(*args, **kwargs)
                try:
                    RedisMarketData.redis.setex(key, RedisMarketData.calculate_expiration_time(), str(value))
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
        self.redis = RedisMarketData()

    @RedisMarketData.cached_tuple
    def ticker_intraday_date(self, ticker: str):
        result = self.cedro.quote(ticker)
        return IntraDayData(Decimal(result['lastTrade'] or result['previous']).quantize(Decimal('0.01')),
                            Decimal(result['previous']).quantize(Decimal('0.01')),
                            Decimal((result['change'])).quantize(Decimal('0.01')),
                            result['company'])

    def tickers_intraday_data(self, tickers):
        attempt = 0
        while attempt < 3:
            try:
                response = {}
                not_in_cache_tickers = []
                for ticker in tickers:
                    cached_value = self.redis.get_intraday_data(ticker)
                    if cached_value:
                        response[ticker] = cached_value
                    else:
                        not_in_cache_tickers.append(ticker)

                logger.info(f'not_in_cache_tickers: {not_in_cache_tickers}')
                if not_in_cache_tickers:
                    quotes = self.cedro.quotes(not_in_cache_tickers)
                    if type(quotes) is not list:
                        quotes = [quotes]
                    for quote in quotes:
                        data = IntraDayData(Decimal(quote['lastTrade'] or quote['previous']).quantize(Decimal('0.01')),
                                            Decimal(quote['previous']).quantize(Decimal('0.01')),
                                            Decimal((quote['change'])).quantize(Decimal('0.01')), quote['company'])
                        ticker = quote['symbol'].upper()
                        response[ticker] = data
                        self.redis.put_intraday_data(ticker, data)
                return response
            except Exception:
                attempt += 1
                logger.exception(f'ATTEMPET {attempt} FAILED.')

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
        logger.info(f'RESULT: {result}')
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))

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

    def find_all(self, subject) -> (Portfolio, [StockConsolidated]):
        result = self._portfolio_table.query(KeyConditionExpression=Key('subject').eq(subject))
        portfolio = None
        stock_consolidated = []
        if not result['Items']:
            logger.info(f"No Portfolio yet for subject: {subject}")
            return
        for item in result['Items']:
            if item['ticker'] == subject:
                portfolio = Portfolio(**item)
            else:
                stock_consolidated.append(StockConsolidated(**item))
        return portfolio, stock_consolidated

    def find_ticker(self, subject, ticker) -> StockConsolidated:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key('subject').eq(subject) & Key('ticker').eq(
                ticker))
        if result['Items']:
            return StockConsolidated(**result['Items'][0])
        logger.info(f"No Portfolio yet for subject: {subject}")

    def find_alias_ticker(self, subject, ticker) -> [StockConsolidated]:
        result = self._portfolio_table.query(IndexName='subjectAliasTickerGlobalIndex',
                                             KeyConditionExpression=Key('subject').eq(subject) & Key('alias_ticker').eq(
                                                 ticker))
        if result['Items']:
            return [StockConsolidated(**i) for i in result['Items']]
        logger.info(f"No Portfolio yet for subject: {subject}")
