import os
from http import HTTPStatus

import requests

from application.enums.ticker_type import TickerType
from application.ports.ticker_info_client import TickerInfoClient
from goatcommons.configuration.system_manager import ConfigurationClient


class RESTTickerInfoClient(TickerInfoClient):
    BASE_URL = os.getenv("TICKER_BASE_API_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("ticker-api-key")

    def get_ticker_code_type(self, ticker_code) -> TickerType:
        response = requests.get(
            f"{self.BASE_URL}/ticker-code/{ticker_code}/type",
            headers={"x-api-key": self.api_key},
        )

        if response.status_code == HTTPStatus.OK:
            return TickerType(response.json()["asset_type"])

    def get_isin_code_from_ticker(self, ticker: str) -> str:
        response = requests.get(
            f"{self.BASE_URL}/ticker/{ticker}/isin",
            headers={"x-api-key": self.api_key},
        )

        if response.status_code == HTTPStatus.OK:
            return response.json()["isin"]

    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        response = requests.get(
            f"{self.BASE_URL}/isin/{isin_code}/ticker",
            headers={"x-api-key": self.api_key},
        )

        if response.status_code == HTTPStatus.OK:
            return response.json()["ticker"]

    def is_ticker_valid(self, ticker: str) -> bool:
        return self.get_isin_code_from_ticker(ticker) is not None
