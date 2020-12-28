import logging
import os

import boto3

logger = logging.getLogger()


class S3DependenciesDownloader:
    BUCKET_NAME = 'chromium-binarys'
    BINARIES = ['chromedriver-exec', 'headless-chromium-exec', 'headless-chromium', 'chromedriver', 'libORBit-2.so.0',
                'libgconf-2.so.4', 'libX11.so.6', 'libglib-2.0.so.0', 'libnss3.so', 'libxcb.so.1', 'libXau.so.6',
                'libsmime3.so', 'libexpat.so.1', 'libsoftokn3.so', 'libfontconfig.so.1', 'libX11-xcb.so.1',
                'swiftshader/libEGL.so', 'swiftshader/libEGL.so.TOC', 'swiftshader/libGLESv2.so',
                'swiftshader/libGLESv2.so.TOC'
                ]

    def __init__(self):
        self.s3 = boto3.client('s3')

    def setup(self):
        if os.path.exists('/tmp/headless-chromium'):
            logger.info("HOT LAMBDA")
        else:
            logger.info("COLD LAMBDA")
            self._create_directories()
            self._download_binaries()

    def _create_directories(self):
        os.system(f'mkdir -p /tmp/swiftshader/')

    def _download_binaries(self):
        for binary in self.BINARIES:
            destination = f'tmp/{binary}'
            self.s3.download_file(self.BUCKET_NAME, binary, destination)
            os.system(f'chmod +x {destination}')
