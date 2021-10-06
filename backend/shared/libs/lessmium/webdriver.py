import logging
import shutil
import uuid

from selenium import webdriver
import os

from lessmium.setup import S3DependenciesDownloader

logger = logging.getLogger()


class LessmiumDriver(webdriver.Chrome):
    def __init__(self):
        S3DependenciesDownloader().setup()
        self._tmp_folder = '/tmp/{}'.format(uuid.uuid4())
        self._create_tmp_dirs()
        super().__init__(chrome_options=self._create_options(), executable_path='/tmp/chromedriver-exec')

    def _create_tmp_dirs(self):
        if not os.path.exists(self._tmp_folder):
            os.makedirs(self._tmp_folder)
        if not os.path.exists(self._tmp_folder + '/user-data'):
            os.makedirs(self._tmp_folder + '/user-data')
        if not os.path.exists(self._tmp_folder + '/data-path'):
            os.makedirs(self._tmp_folder + '/data-path')
        if not os.path.exists(self._tmp_folder + '/cache-dir'):
            os.makedirs(self._tmp_folder + '/cache-dir')

    def _create_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280x1696')
        options.add_argument('--user-data-dir={}'.format(self._tmp_folder + '/user-data'))
        options.add_argument('--hide-scrollbars')
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--v=99')
        options.add_argument('--single-process')
        options.add_argument('--data-path={}'.format(self._tmp_folder + '/data-path'))
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--homedir={}'.format(self._tmp_folder))
        options.add_argument('--disk-cache-dir={}'.format(self._tmp_folder + '/cache-dir'))
        options.binary_location = "/tmp/headless-chromium-exec"
        return options

    def __del__(self):
        self.quit()
        shutil.rmtree(self._tmp_folder)
        folder = '/tmp'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if 'core.headless-chromi' in file_path and os.path.exists(file_path) and os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f'Error deleting chrome files: {str(e)}')
