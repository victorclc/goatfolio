import datetime
import os

import requests

from domain.models.ticker_transformation import TickerTransformation
from goatcommons.configuration.system_manager import ConfigurationClient


class RESTCorporateEventsClient:
    BASE_URL = os.getenv("CORPORATE_EVENTS_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("corporate-events-api-key")

    def get_ticker_transformation(
        self, ticker: str, date: datetime.date
    ) -> TickerTransformation:
        url = f"{self.BASE_URL}/transformations?ticker={ticker}&dateFrom={date.strftime('%Y%m%d')}"
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return TickerTransformation(**response.json())
