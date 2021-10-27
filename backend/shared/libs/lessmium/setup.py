import logging
import os

import boto3

logger = logging.getLogger()


class S3DependenciesDownloader:
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    BINARIES = ["headless-chromium"]

    def __init__(self):
        self.s3 = boto3.client("s3")

    def setup(self):
        if os.path.exists("/tmp/headless-chromium"):
            logger.info("HOT LAMBDA")
        else:
            logger.info("COLD LAMBDA")
            self._prepare_resources()
            self._download_binaries()

    def _prepare_resources(self):
        os.system("mkdir -p /tmp/usr/share/fonts")
        os.system("cp -r shared/libs/lessmium/resources/fonts/* /tmp/usr/share/fonts/")
        os.system(
            "cp -r shared/libs/lessmium/resources/lib/* shared/libs/lessmium/resources/bin/* /tmp && chmod -R +x /tmp/*"
        )

    def _download_binaries(self):
        for binary in self.BINARIES:
            destination = f"/tmp/{binary}"
            logger.info(f"Downloading {binary} to {destination}")
            self.s3.download_file(self.BUCKET_NAME, binary, destination)
            os.system(f"chmod +x {destination}")
