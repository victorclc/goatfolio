import logging
from http import HTTPStatus

import requests

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger()

metrics = Metrics(namespace="PerformanceAPI", service="CedroTechClient")


class CedroMarketDataClient:
    __API_LOGIN = 'majesty'
    __API_PASSWORD = '102030'
    __SIGN_IN_URL = 'https://webfeeder.cedrotech.com/SignIn'
    __QUOTE_URL = 'https://webfeeder.cedrotech.com/services/quotes/quote/'

    def __init__(self):
        self.session = requests.sessions.session()
        self.is_authenticated = False

    def __authenticate(self):
        logger.info(f'API Authenticating.')
        response = self.session.post(self.__SIGN_IN_URL,
                                     data={'login': self.__API_LOGIN, 'password': self.__API_PASSWORD},
                                     headers={"content-type": "application/x-www-form-urlencoded",
                                              'Connection': 'keep-alive'})
        if response.status_code == HTTPStatus.OK:
            logger.info("Cedro Authenticated sucessfully")
            self.is_authenticated = response.content
        else:
            logger.error(f'Authentication error: {response.status_code} - {response.content}')

    @metrics.log_metrics
    def quote(self, ticker):
        if not self.is_authenticated:
            self.__authenticate()
        response = self.session.get(self.__QUOTE_URL + ticker)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logger.info("Unauthorized on cedro call, marking as not authenticated.")
            self.is_authenticated = False
        if response.status_code == HTTPStatus.OK:
            metrics.add_metric(name="SuccessfulAPIHits", unit=MetricUnit.Count, value=1)
            return response.json()
        logger.error(f'QUOTES ERROR: {response.status_code} - {response.content}')
        metrics.add_metric(name="FailedAPIHits", unit=MetricUnit.Count, value=1)
        # TODO PUT A THROW HERE

    @metrics.log_metrics
    def quotes(self, tickers):
        if not self.is_authenticated:
            self.__authenticate()
        quotes = ''
        for ticker in tickers:
            quotes += f'{ticker}/'
        response = self.session.get(self.__QUOTE_URL + quotes)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logger.info("Unauthorized on cedro call, marking as not authenticated.")
            self.is_authenticated = False

        try:
            json = response.json()
            if type(json) is not list:
                metrics.add_metric(name="SuccessfulAPIHits", unit=MetricUnit.Count, value=len(tickers))
                json = [json]
            return json
        except Exception as e:
            metrics.add_metric(name="FailedAPIHits", unit=MetricUnit.Count, value=1)
            logger.exception(f'QUOTES ERROR: {response}', e)
            raise e
