from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from auroradata.aurora import AuroraData

if __name__ == '__main__':
    response = \
        requests.get('https://query1.finance.yahoo.com/v7/finance/chart/^BVSP?range=max&interval=1mo').json()['chart'][
            'result'][0]

    quote = response['indicators']['quote'][0]
    timestamp = response['timestamp'][:-1]
    sql_statements_data = []

    secret = "arn:aws:secretsmanager:us-east-2:831967415635:secret:rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres-z9xJqf"
    cluster = "arn:aws:rds:us-east-2:831967415635:cluster:serverless-goatfolio-dev-marketdatardscluster-dq6ryzdhjru0"
    database = "marketdata"

    aurora_data = AuroraData(cluster, secret, database)
    sql = 'INSERT INTO b3_monthly_chart (ticker, candle_date, company_name, open_price, close_price, max_price, min_price, volume) values (:ticker, :candle_date, :company_name, :open_price, :close_price, :max_price, :min_price, :volume)'
    for i in range(len(timestamp)):
        date = datetime.fromtimestamp(timestamp[i])
        if date.day != 1:
            date = datetime(date.year, date.month, 1) + relativedelta(months=1)

        entry = [
            {'name': 'ticker', 'value': {'stringValue': 'IBOVESPA'}},
            {'name': 'candle_date', 'typeHint': 'DATE', 'value': {'stringValue': date.strftime('%Y-%m-%d')}},
            {'name': 'company_name', 'value': {'stringValue': 'Indice Ibovespa'}},
            {'name': 'open_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['open'][i]}"}},
            {'name': 'close_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['close'][i]}"}},
            {'name': 'max_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['high'][i]}"}},
            {'name': 'min_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['low'][i]}"}},
            {'name': 'volume', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['volume'][i]}"}}
        ]
        sql_statements_data.append(entry)

    print(sql_statements_data)
    aurora_data.batch_execute_statement(sql, sql_statements_data)
