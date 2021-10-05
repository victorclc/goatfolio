import datetime
from dataclasses import dataclass
from decimal import Decimal
from itertools import groupby

import psycopg2

from auroradata.aurora import AuroraData


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


def fetch_distinct_tickers(cursor):
    cursor.execute('SELECT DISTINCT ticker from b3_daily_chart')
    return [t[0] for t in cursor.fetchall()]


def fetch_ticker_investments(cursor, ticker):
    cursor.execute(f'SELECT * from b3_daily_chart where ticker = \'{ticker}\' order by candle_date ')
    result = groupby([B3Chart(*t) for t in cursor.fetchall()],
                     lambda c: datetime.date(c.candle_date.year, c.candle_date.month, 1))
    ret = {}
    for key, value in result:
        ret[key] = list(value)
    return ret


if __name__ == '__main__':
    secret = "arn:aws:secretsmanager:us-east-2:831967415635:secret:rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres-z9xJqf"
    cluster = "arn:aws:rds:us-east-2:831967415635:cluster:serverless-goatfolio-dev-marketdatardscluster-dq6ryzdhjru0"
    database = "marketdata"
    aurora_data = AuroraData(cluster, secret, database)
    # aurora_data.execute_statement('delete from b3_monthly_chart')
    # raise Exception
    con = psycopg2.connect(host='localhost', database='postgres',
                           user='postgres', password='postgres')
    cur = con.cursor()
    tickers = fetch_distinct_tickers(cur)

    sql = 'INSERT INTO b3_monthly_chart (ticker, candle_date, company_name, open_price, close_price, average_price, max_price, min_price, volume) values (:ticker, :candle_date, :company_name, :open_price, :close_price, :average_price, :max_price, :min_price, :volume)'

    for ticker in tickers:
        print(f'Processing ticker: {ticker}')
        sql_parameter_sets = []
        daily_grouped = fetch_ticker_investments(cur, ticker)
        for year_month, investments in daily_grouped.items():
            company_name = investments[0].company_name
            open_price = investments[0].open_price
            close_price = investments[-1].close_price
            max_price = max([i.max_price for i in investments])
            min_price = min([i.min_price for i in investments])
            average_price = (sum([i.average_price for i in investments]) / len(investments)).quantize(Decimal('0.01'))
            volume = sum([i.volume for i in investments])

            entry = [
                {'name': 'ticker', 'value': {'stringValue': ticker}},
                {'name': 'candle_date', 'typeHint': 'DATE', 'value': {'stringValue': f"{year_month}"}},
                {'name': 'company_name', 'value': {'stringValue': company_name}},
                {'name': 'open_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{open_price}'}},
                {'name': 'close_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{close_price}'}},
                {'name': 'average_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{average_price}'}},
                {'name': 'max_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{max_price}'}},
                {'name': 'min_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{min_price}'}},
                {'name': 'volume', 'typeHint': 'DECIMAL', 'value': {'stringValue': f'{volume}'}},
            ]
            sql_parameter_sets.append(entry)
        print(f'Entrys: {len(sql_parameter_sets)}')
        print(aurora_data.batch_execute_statement(sql=sql, parameter_sets=sql_parameter_sets))
