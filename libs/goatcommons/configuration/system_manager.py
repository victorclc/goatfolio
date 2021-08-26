import boto3


class ConfigurationClient:
    def __init__(self):
        self.client = boto3.client('ssm')

    def get_secret(self, key):
        resp = self.client.get_parameter(
            Name=key,
            WithDecryption=True
        )
        return resp['Parameter']['Value']
