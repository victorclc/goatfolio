import boto3 as boto3


class B3CotaHistBucket:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def download_file(self, bucket, file_path):
        destination = f'/tmp/{file_path}'
        self.s3.download_file(bucket, file_path, destination)
        return destination
