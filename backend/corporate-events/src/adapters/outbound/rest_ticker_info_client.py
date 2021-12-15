import os

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

        return TickerType(response.json()["asset_type"])
