import os
from collections import namedtuple
from datetime import datetime, date
from decimal import Decimal
from itertools import groupby
from typing import List

import boto3
import requests

from goatcommons.models import Investment
from goatcommons.utils import InvestmentUtils

IntraDayData = namedtuple('IntraDayData', 'price change')
MonthlyData = namedtuple('MonthlyData', 'date open close change')


class MarketData:
    """
        MarketData its responsible to join information from MarketStack and YahooFinance API's
        market stack has a great api, but only have info until yesterday (D-1)
        yahoo finance has both now and historical data, but the historical data for some tickers are not reliable
    """

    # todo update market_stack info with yahoo
    def __init__(self):
        self.yahoo = self.YahooData()
        self.market_stack = self.MarketStackData()

    def ticker_monthly_data(self, ticker):
        return self.market_stack.get_monthly_data(ticker)

    class YahooData:
        INTRA_DAY_URL = "https://query2.finance.yahoo.com/v7/finance/options/{0}.SA"
        HISTORICAL_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{0}?range={1}&interval={2}"

        def get_intraday_data(self, ticker):
            url = self.INTRA_DAY_URL.format(ticker)
            result = requests.get(url).json()['optionChain']['result'][0]
            return IntraDayData(result['regularMarketPrice'], result['regularMarketChangePercent'])

    class MarketStackData:
        EOD_URL = "http://api.marketstack.com/v1/eod/"

        DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

        def __init__(self):
            self.api_key = os.getenv("MARKET_STACK_API_KEY")

        def get_monthly_data(self, ticker):
            params = {
                'access_key': self.api_key,
                'symbols': '{}.BVMF'.format(ticker),
                'limit': 365
            }
            result = requests.get(self.EOD_URL, params).json()
            monthly_data = []

            for month, candles in groupby(map(self._parse_eod_data, result['data']),
                                          key=lambda x: x['date'].month):
                candles = list(candles)
                _open = candles[-1]['open']
                close = candles[0]['close']
                monthly_data.append(MonthlyData(date=date(candles[0]['date'].year, month, 1), open=_open, close=close,
                                                change=Decimal(((close - _open) * 100) / _open).quantize(
                                                    Decimal('0.01'))))
            return monthly_data

        def _parse_eod_data(self, data):
            new_date = dict(data)
            new_date['date'] = datetime.strptime(data['date'], self.DATE_FORMAT)
            new_date['open'] = Decimal(data['open']).quantize(Decimal('0.01'))
            new_date['close'] = Decimal(data['close']).quantize(Decimal('0.01'))
            return new_date


class InvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource('dynamodb').Table('Investments')

    def find_by_subject(self, subject) -> List[Investment]:
        result = self.__investments_table.query(KeyConditionExpression=Key('subject').eq(subject))
        return list(map(lambda i: InvestmentUtils.load_model_by_type(i['type'], i), result['Items']))
