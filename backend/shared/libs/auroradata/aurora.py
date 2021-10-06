from contextlib import contextmanager
from http import HTTPStatus

import boto3


class AuroraData:
    def __init__(self, cluster_arn, secret_arn, database):
        self._client = boto3.client('rds-data')
        self.cluster_arn = cluster_arn
        self.secret_arn = secret_arn
        self.database = database

    def get_params(self, include_database_param=False):
        params = {
            'secretArn': self.secret_arn,
            'resourceArn': self.cluster_arn
        }
        if include_database_param:
            params['database'] = self.database
        return params

    def execute_statement(self, sql, transaction_id=None):
        params = self.get_params(include_database_param=True)
        params['sql'] = sql
        if transaction_id:
            params['transactionId'] = transaction_id
        response = self._client.execute_statement(**params)
        print(f'execute_statement: {response}')
        return self._client.execute_statement(**params)

    def batch_execute_statement(self, sql, parameter_sets=None, transaction_id=None):
        params = self.get_params(include_database_param=True)
        params['sql'] = sql
        if transaction_id:
            params['transactionId'] = transaction_id
        if parameter_sets:
            params['parameterSets'] = parameter_sets
        return self._client.batch_execute_statement(**params)

    def begin_transaction(self, schema='public'):
        params = self.get_params(include_database_param=True)
        params['schema'] = schema
        return self._client.begin_transaction(**params)

    def commit_transaction(self, transaction_id):
        params = self.get_params()
        params['transactionId'] = transaction_id
        return self._client.commit_transaction(secretArn=self.secret_arn, resourceArn=self.cluster_arn,
                                               transactionId=transaction_id)

    def rollback_transaction(self, transaction_id):
        params = self.get_params()
        params['transactionId'] = transaction_id
        return self._client.rollback_transaction(secretArn=self.secret_arn, resourceArn=self.cluster_arn,
                                                 transactionId=transaction_id)

    @contextmanager
    def open_transaction(self, schema='public'):
        transaction_id = None
        try:
            begin_response = self.begin_transaction(schema=schema)
            print(f"begin_transaction response: {begin_response}")
            assert begin_response['ResponseMetadata']['HTTPStatusCode'] == HTTPStatus.OK
            transaction_id = begin_response['transactionId']
            yield self.TransactionWriter(transaction_id, self)
        except Exception:
            self.rollback_transaction(transaction_id)
            transaction_id = None
            raise
        finally:
            if transaction_id:
                self.commit_transaction(transaction_id)

    class TransactionWriter:
        def __init__(self, transaction_id, aurora_data):
            assert transaction_id
            self.transaction_id = transaction_id
            self.aurora_data = aurora_data

        def execute_statement(self, sql):
            response = self.aurora_data.execute_statement(sql=sql, transaction_id=self.transaction_id)
            print(f"execute_statement response: {response}")
            return response

        def batch_execute_statement(self, sql):
            response = self.aurora_data.batch_execute_statement(sql=sql, transaction_id=self.transaction_id)
            print(f"execute_statement response: {response}")
            return response


if __name__ == '__main__':
    # statement = "INSERT INTO b3_monthly_chart (ticker, candle_date, company_name, open_price, close_price, average_price, max_price, min_price, volume) values ('CCPR3', '2021-03-01', 'CYRE COM-CCP', 11.25, 11.50, 10.93, 10.21, 11.61, 220.60)"
    # secret = "arn:aws:secretsmanager:us-east-2:831967415635:secret:rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres-z9xJqf"
    # cluster = "arn:aws:rds:us-east-2:831967415635:cluster:serverless-goatfolio-dev-marketdatardscluster-dq6ryzdhjru0"
    # database = "marketdata"
    # aurora_data = AuroraData(cluster, secret, database)
    # print(aurora_data.execute_statement("DELETE FROM b3_monthly_chart"))
    # with aurora_data.open_transaction() as transaction_writer:
    #     transaction_writer.execute_statement(statement)
    # # print(aurora_data.execute_statement('SELECT * FROM b3_monthly_chart'))
    pass
