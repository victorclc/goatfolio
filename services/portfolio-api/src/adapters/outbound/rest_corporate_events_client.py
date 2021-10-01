import datetime

import requests

from domain.models.ticker_transformation import TickerTransformation


class RESTCorporateEventsClient:
    BASE_URL = "https://dev.goatfolio.com.br/corporate-events"

    def __init__(self):
        # config = ConfigurationClient()
        # key = config.get_secret("corporate-events-key")
        self.api_key = "MV9Bmm4WA892LuRVQmb1c6p0kRQlUQqb9KXYUNsL"

    def get_ticker_transformation(self, ticker: str, date: datetime.date) -> TickerTransformation:
        url = f"{self.BASE_URL}/transformations?ticker={ticker}&dateFrom={date.strftime('%Y%m%d')}"
        response = requests.get(url, headers={"x-api-key": self.api_key})

        return TickerTransformation(**response.json())
