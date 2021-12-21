import datetime as dt
from dataclasses import dataclass, asdict
from typing import List

import certifi

from application.config.certificates import certificates
from application.models.companies_updates import CompaniesUpdates, CompanyDetails, CompanySupplement
from application.ports.fetch_events_client import FetchEventsClient
import requests
import base64
import re

import goatcommons.utils.json as jsonutils


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def snake_case_dict(_dict: dict):
    new = {}
    for key, value in _dict.items():
        if type(value) == list:
            value = [snake_case_dict(i) if type(i) == dict else i for i in value]
        if type(value) == dict:
            value = snake_case_dict(value)
        new[to_snake_case(key)] = value
    return new


@dataclass
class IssuingCompanyRequest:
    issuingCompany: str
    language: str = "pt-br"


class RESTB3EventsClient(FetchEventsClient):
    LATEST_EVENTS_URL = "https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0="
    STOCK_SUP_URL = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompany"
    BDR_SUP_URL = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompanyBDR"
    FII_SUP_URL = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompanyFunds"

    def __init__(self):
        with open(certifi.where(), "a") as fp:
            fp.write(certificates)

    def fetch_latest_events_updates(self) -> List[CompaniesUpdates]:
        response = requests.get(self.LATEST_EVENTS_URL)

        return [
            CompaniesUpdates(
                date=dt.datetime.strptime(i["date"], "%d/%m/%Y").date(),
                companies=[
                    CompanyDetails(
                        company_name=c["companyName"],
                        trading_name=c["tradingName"],
                        ticker_code=c["code"],
                        segment=c["segment"],
                        code_cvm=c["codeCvm"],
                        url=c["url"],
                    )
                    for c in i["results"]
                ],
            )
            for i in response.json()
        ]

    def fetch_companies_updates_from_date(self, _date: dt.date) -> List[CompanyDetails]:
        return list(
            filter(lambda c: c.date == _date, self.fetch_latest_events_updates())
        )[0].companies

    def get_stock_supplement(self, ticker_code: str) -> CompanySupplement:
        response = requests.get(
            f"{self.STOCK_SUP_URL}/{self.encoded_supplement_request(ticker_code)}"
        )

        return self.parse_company_supplement(response.json()[0])

    def get_bdr_supplement(self, ticker_code: str) -> CompanySupplement:
        response = requests.get(
            f"{self.BDR_SUP_URL}/{self.encoded_supplement_request(ticker_code)}"
        )

        return self.parse_company_supplement(response.json()[0])

    def get_fii_supplement(self, ticker_code: str) -> CompanySupplement:
        response = requests.get(
            f"{self.FII_SUP_URL}/{self.encoded_supplement_request(ticker_code)}"
        )

        return self.parse_company_supplement(response.json()[0])

    @staticmethod
    def encoded_supplement_request(ticker_code: str):
        request = IssuingCompanyRequest(ticker_code.upper())
        return str(base64.b64encode(
            jsonutils.dump(asdict(request)).encode("utf-8")
        ), "utf-8")

    @staticmethod
    def parse_company_supplement(json: dict) -> CompanySupplement:
        # new_json = {to_snake_case(k): v for k, v in json.items()}
        tmp = snake_case_dict(json)

        return CompanySupplement(cash_dividends=tmp["cash_dividends"],
                                 stock_dividends=tmp["stock_dividends"],
                                 subscriptions=tmp["subscriptions"])
