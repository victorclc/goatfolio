import os
from http import HTTPStatus

import requests

from application.exceptions.ticker_validation_error import TickerValidationError
from goatcommons.configuration.system_manager import ConfigurationClient


class RestTickerInfoClient:
    BASE_URL = os.getenv("TICKER_BASE_API_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("ticker-api-key")

    def is_ticker_valid(self, ticker) -> bool:
        response = requests.get(
            f"{self.BASE_URL}/ticker/{ticker}",
            headers={"x-api-key": self.api_key},
        )
        status_code = response.status_code
        if status_code not in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]:
            raise TickerValidationError(
                f"Error validating ticker, status_code: {status_code}, content: {response.content}"
            )
        return response.status_code == HTTPStatus.OK
