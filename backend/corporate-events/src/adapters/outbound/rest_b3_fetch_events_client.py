import datetime as dt
from dataclasses import dataclass, asdict
from typing import List

from application.models.companies_updates import CompaniesUpdates, CompanyDetails
from application.ports.fetch_events_client import FetchEventsClient
import requests
import base64

import goatcommons.utils.json as jsonutils


@dataclass
class IssuingCompanyRequest:
    issuingCompany: str
    language: str = "pt-br"


class RESTB3EventsClient(FetchEventsClient):
    def fetch_latest_events_updates(self) -> List[CompaniesUpdates]:
        response = requests.get(
            "https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0="
        )
        # return response.json()
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

    def get_stock_supplement(self, ticker_code: str):
        request = IssuingCompanyRequest(ticker_code.upper())
        encoded_request = base64.b64encode(
            jsonutils.dump(asdict(request)).encode("utf-8")
        )

        response = requests.get(
            f"https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompany/{str(encoded_request, 'utf-8')}"
        )

        return response.json()
