import datetime
import os
from typing import List

import requests

from domain.performance.ticker_transformation import TickerTransformation
from domain.corporate_events.earnings_in_assets_event import EarningsInAssetCorporateEvent
from goatcommons.configuration.system_manager import ConfigurationClient


class RESTCorporateEventsClient:
    BASE_URL = os.getenv("CORPORATE_EVENTS_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("corporate-events-api-key")

    def get_ticker_transformation(
        self, subject: str, ticker: str, date: datetime.date
    ) -> TickerTransformation:
        url = f"{self.BASE_URL}/transformations?ticker={ticker}&dateFrom={date.strftime('%Y%m%d')}&subject={subject}"
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return TickerTransformation(**response.json())

    def corporate_events_from_date(
        self, subject: str, ticker: str, date: datetime.date
    ) -> List[EarningsInAssetCorporateEvent]:
        url = (
            f"{self.BASE_URL}/events?ticker={ticker}&dateFrom={date.strftime('%Y%m%d')}&subject={subject}"
        )
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return [EarningsInAssetCorporateEvent(**e) for e in response.json()]
