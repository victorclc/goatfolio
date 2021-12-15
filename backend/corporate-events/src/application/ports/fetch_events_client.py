import abc
from typing import List
import datetime as dt

from application.models.companies_updates import CompaniesUpdates, CompanyDetails


class FetchEventsClient(abc.ABC):
    @abc.abstractmethod
    def fetch_latest_events_updates(self) -> List[CompaniesUpdates]:
        ...

    @abc.abstractmethod
    def fetch_companies_updates_from_date(self, _date: dt.date) -> List[CompanyDetails]:
        ...

    @abc.abstractmethod
    def get_stock_supplement(self, ticker_code: str):
        ...
