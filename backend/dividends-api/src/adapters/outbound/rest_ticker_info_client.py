import os
from http import HTTPStatus

import requests

from goatcommons.configuration.system_manager import ConfigurationClient


class RestTickerInfoClient:
    BASE_URL = os.getenv("TICKER_BASE_API_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("ticker-api-key")

    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        response = requests.get(
            f"{self.BASE_URL}/isin/{isin_code}/ticker",
            headers={"x-api-key": self.api_key},
        )

        if response.status_code == HTTPStatus.OK:
            return response.json()["ticker"]
