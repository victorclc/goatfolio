from collections import namedtuple
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import List

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from yahooquery import Ticker

from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils
from models import Portfolio, CandleData

# logging.basicConfig(level=logging.DEBUG)

IntraDayData = namedtuple('IntraDayData', 'price prev_close_price change name')
MonthData = namedtuple('MonthlyData', 'open close')


class MarketData:
    def __init__(self):
        self.repo = MarketDataRepository()
        self.yahoo_ticker = None

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
        return []

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


if __name__ == '__main__':
    repo = MarketDataRepository()
    _result = repo.find_by_ticker_from_date('ITSA4', date(2021, 1, 13))
    # _result = repo.find_by_ticker_from_date(['TIET11', 'AESB3'], date(2021, 3, 13))
    print(_result)


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
