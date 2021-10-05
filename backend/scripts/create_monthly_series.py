import datetime
from dataclasses import dataclass
from decimal import Decimal
from itertools import groupby

import psycopg2


@dataclass
class B3Chart:
    ticker: str
    candle_date: datetime.date
    company_name: str
    open_price: Decimal
    close_price: Decimal
    max_price: Decimal
    min_price: Decimal
    average_price: Decimal
    best_ask: Decimal = None
    best_bid: Decimal = None
    volume: Decimal = None

    def create_statement(self):
        return f'INSERT INTO b3_monthly_chart ' \
               f'(ticker, candle_date, company_name, open_price, close_price, average_price, max_price, min_price, volume) values ' \
               f'(\'{self.ticker}\', \'{self.candle_date}\', \'{self.company_name}\', {self.open_price}, {self.close_price}, {self.average_price}, {self.min_price}, {self.max_price}, {self.volume});\n'


def fetch_distinct_tickers(cursor):
    cursor.execute('SELECT DISTINCT ticker from b3_daily_chart')
    return [t[0] for t in cursor.fetchall()]


def fetch_ticker_investments(cursor, ticker):
    cursor.execute(f'SELECT * from b3_daily_chart where ticker = \'{ticker}\' order by candle_date ')
    result = groupby([B3Chart(*t) for t in cursor.fetchall()],
                     lambda c: datetime.date(c.candle_date.year, c.candle_date.month, 1))
    ret = {}
    today = datetime.datetime.now()
    for key, value in result:
        if key.year == today.year and key.month == today.month:
            ret[key] = list(value)
    return ret


if __name__ == '__main__':
    con = psycopg2.connect(host='localhost', database='postgres',
                           user='postgres', password='postgres')
    cur = con.cursor()
    tickers = fetch_distinct_tickers(cur)

    with open('monthly_data_march.sql', 'w+') as fp:
        for ticker in tickers:
            daily_grouped = fetch_ticker_investments(cur, ticker)
            for year_month, investments in daily_grouped.items():
                company_name = investments[0].company_name
                open_price = investments[0].open_price
                close_price = investments[-1].close_price
                max_price = max([i.max_price for i in investments])
                min_price = min([i.min_price for i in investments])
                average_price = (sum([i.average_price for i in investments]) / len(investments)).quantize(Decimal('0.01'))
                volume = sum([i.volume for i in investments])
                month_chart = B3Chart(ticker, year_month, company_name, open_price, close_price, max_price, min_price,
                                      average_price, volume=volume)
                fp.write(month_chart.create_statement())

    con.close()
