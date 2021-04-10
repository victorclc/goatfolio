import logging

from adapters import B3CotaHistBucket, CotaHistRepository
from models import B3DailySeries, BDICodes

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CotaHistTransformerCore:
    def __init__(self):
        self.bucket = B3CotaHistBucket()
        self.repo = CotaHistRepository()

    def transform_cota_hist(self, bucket_name, file_path):
        downloaded_path = self.bucket.download_file(bucket_name, file_path)
        series = []
        with open(downloaded_path, 'r') as fp:
            for line in fp:
                if line.startswith('99COTAHIST') or line.startswith('00COTAHIST'):
                    continue
                data = B3DailySeries(line)
                if data.codigo_bdi not in [BDICodes.STOCK, BDICodes.FII, BDICodes.ETF]:
                    continue
                series.append(data.row)

        self.repo.save(series)
        self.bucket.move_file_to_archive(bucket_name, file_path)


if __name__ == '__main__':
    # secrets_client = boto3.client("secretsmanager")
    # result = secrets_client.get_secret_value(SecretId='rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres')
    # print(result)
    # secret = JsonUtils.load(result['SecretString'])
    # _username = secret['username']
    # _password = secret['password']
    # _port = secret['port']
    # _host = secret['host']
    core = CotaHistTransformerCore()
    core.transform_cota_hist(None, None)
