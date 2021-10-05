import logging
import os
from io import StringIO

import boto3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class S3CorporateEventsFileStorage:
    def __init__(self):
        self.s3 = boto3.client("s3")
        self._downloaded_files = []
        self.bucket_name = os.getenv("CORPORATE_BUCKET")

    def download(self, file: str) -> str:
        destination = f"/tmp/{file.split('/')[-1]}"
        logger.info(f"Downloading to: {destination}")
        self.s3.download_file(self.bucket_name, file, destination)
        logger.info(f"Download finish")
        self._downloaded_files.append(destination)
        return destination

    def upload(self, buffer: StringIO, file_name: str):
        logger.info(f"Saving {file_name} on s3:::{self.bucket_name}")
        self.s3.put_object(
            Body=buffer.getvalue(), Bucket=self.bucket_name, Key=f"new/{file_name}"
        )

    def move_to_archive(self, file_path: str):
        file_name = self._file_name_from_path(file_path)
        self.s3.copy_object(
            Bucket=self.bucket_name,
            CopySource=f"{self.bucket_name}/{file_path}",
            Key=f"archive/{file_name}",
        )
        self.s3.delete_object(Bucket=self.bucket_name, Key=file_path)

    def move_to_unprocessed(self, file_path: str):
        file_name = self._file_name_from_path(file_path)
        self.s3.copy_object(
            Bucket=self.bucket_name,
            CopySource=f"{self.bucket_name}/{file_path}",
            Key=f"unprocessed/{file_name}",
        )
        self.s3.delete_object(Bucket=self.bucket_name, Key=file_path)

    @staticmethod
    def _file_name_from_path(path: str):
        return path.split("/")[-1]

    def __del__(self):
        for file in self._downloaded_files:
            os.system(f"rm -f {file}")
