import logging

import boto3 as boto3

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class B3CotaHistBucket:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def download_file(self, bucket, file_path):
        destination = f"/tmp/{file_path.split('/')[-1]}"
        logger.info(f'Downloading to: {destination}')
        self.s3.download_file(bucket, file_path, destination)
        logger.info(f'Download finish')
        return destination

    def move_file_to_archive(self, bucket, file_path):
        self.s3.copy_object(Bucket=bucket, CopySource=f'{bucket}/{file_path}', Key=f"archive/{file_path}")
        self.s3.delete_object(Bucket=bucket, Key=file_path)
