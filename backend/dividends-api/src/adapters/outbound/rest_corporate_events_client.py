import datetime
import os
from typing import List

import requests

from application.models.dividends import CashDividends
from goatcommons.configuration.system_manager import ConfigurationClient


class RESTCorporateEventsClient:
    BASE_URL = os.getenv("CORPORATE_EVENTS_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("corporate-events-api-key")

    def get_cash_dividends(
            self, date: datetime.date
    ) -> List[CashDividends]:
        url = f"{self.BASE_URL}/cash-dividends?date={date.strftime('%Y%m%d')}"
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return [CashDividends(**d) for d in response.json()]

    def get_all_previous_symbols(self, isin_code: str) -> List[str]:
        url = f"{self.BASE_URL}/previous-symbols?isin_code={isin_code}"
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return response.json()

    def get_cash_dividends_for_ticker(
            self, ticker: str, from_date: datetime.date
    ) -> List[CashDividends]:
        url = f"{self.BASE_URL}/cash-dividends/{ticker}?from_date={from_date.strftime('%Y%m%d')}"
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return [CashDividends(**d) for d in response.json()]
