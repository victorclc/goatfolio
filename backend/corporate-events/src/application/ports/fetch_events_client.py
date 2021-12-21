import abc
from typing import List
import datetime as dt

from application.models.companies_updates import CompaniesUpdates, CompanyDetails, CompanySupplement


class FetchEventsClient(abc.ABC):
    @abc.abstractmethod
    def fetch_latest_events_updates(self) -> List[CompaniesUpdates]:
        ...

    @abc.abstractmethod
    def fetch_companies_updates_from_date(self, _date: dt.date) -> List[CompanyDetails]:
        ...

    @abc.abstractmethod
    def get_stock_supplement(self, ticker_code: str) -> CompanySupplement:
        ...

    @abc.abstractmethod
    def get_bdr_supplement(self, ticker_code: str) -> CompanySupplement:
        ...

    @abc.abstractmethod
    def get_fii_supplement(self, ticker_code: str) -> CompanySupplement:
        ...
