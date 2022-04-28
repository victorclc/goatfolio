import base64
import datetime
from dataclasses import dataclass, asdict
from decimal import Decimal
from http import HTTPStatus
from typing import List

import boto3
from boto3.dynamodb.conditions import Key
import os
import requests
from enum import Enum
import re

ticker_data = boto3.resource("dynamodb").Table("TickerInfo")

done = False
start_key = None

DATE_FORMAT = "%d/%m/%Y"

_DATE_FORMAT = "%Y%m%d"

import json
from decimal import Decimal


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        # if isinstance(obj, datetime):
        #     return int(obj.timestamp())

        return json.JSONEncoder.default(self, obj)


def dump(_dict):
    return json.dumps(_dict, cls=CustomEncoder)


def load(json_str):
    return json.loads(json_str, parse_float=Decimal)


@dataclass
class CashDividendsEntity:
    asset_issued: str
    payment_date: datetime.date
    rate: Decimal
    related_to: str
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str = ""
    id: str = None

    def __post_init__(self):
        if isinstance(self.payment_date, str):
            self.payment_date = datetime.datetime.strptime(self.payment_date, _DATE_FORMAT).date()
        if isinstance(self.approved_on, str):
            self.approved_on = datetime.datetime.strptime(self.approved_on, _DATE_FORMAT).date()
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, _DATE_FORMAT).date()
        if not isinstance(self.rate, Decimal):
            self.rate = Decimal(self.rate).quantize(Decimal("0.00000000001"))
        if not self.id:
            self.id = f"{self.payment_date.strftime(_DATE_FORMAT)}" \
                      f"#{self.label}#{self.approved_on.strftime(_DATE_FORMAT)}" \
                      f"#{self.last_date_prior.strftime(_DATE_FORMAT)}" \
                      f"#{self.rate}" \
                      f"#{self.isin_code}"

    def to_dict(self):
        return {
            **self.__dict__,
            "payment_date": self.payment_date.strftime(_DATE_FORMAT),
            "approved_on": self.approved_on.strftime(_DATE_FORMAT),
            "last_date_prior": self.last_date_prior.strftime(_DATE_FORMAT),
        }


@dataclass
class CashDividends:
    asset_issued: str
    payment_date: datetime.date
    rate: Decimal
    related_to: str
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str = ""

    def __post_init__(self):
        if isinstance(self.payment_date, str):
            self.payment_date = datetime.datetime.strptime(self.payment_date, DATE_FORMAT).date()
        if isinstance(self.approved_on, str):
            self.approved_on = datetime.datetime.strptime(self.approved_on, DATE_FORMAT).date()
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, DATE_FORMAT).date()
        if isinstance(self.rate, str):
            self.rate = Decimal(self.rate.replace(".", "").replace(",", ".")).quantize(Decimal("0.00000000001"))
        if not isinstance(self.rate, Decimal):
            self.rate = Decimal(self.rate).quantize(Decimal("0.00000000001"))

    def to_dict(self):
        return {
            **self.__dict__,
            "payment_date": self.payment_date.strftime(DATE_FORMAT),
            "approved_on": self.approved_on.strftime(DATE_FORMAT),
            "last_date_prior": self.last_date_prior.strftime(DATE_FORMAT),
        }

    def to_entity(self) -> CashDividendsEntity:
        return CashDividendsEntity(**self.__dict__)


@dataclass
class StockDividends:
    asset_issued: str
    factor: Decimal
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str

    def __post_init__(self):
        if type(self.approved_on) == str:
            self.approved_on = datetime.datetime.strptime(self.approved_on, DATE_FORMAT).date()
        if type(self.last_date_prior) == str:
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, DATE_FORMAT).date()
        if type(self.factor) == str:
            self.factor = Decimal(self.factor.replace(".", "").replace(",", "."))


@dataclass
class Subscriptions:
    asset_issued: str
    percentage: Decimal
    price_unit: Decimal
    trading_period: str
    subscription_date: datetime.date
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str

    def __post_init__(self):
        if type(self.subscription_date) == str:
            self.subscription_date = datetime.datetime.strptime(self.subscription_date, DATE_FORMAT).date()
        if type(self.approved_on) == str:
            self.approved_on = datetime.datetime.strptime(self.approved_on, DATE_FORMAT).date()
        if type(self.last_date_prior) == str:
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, DATE_FORMAT).date()
        if type(self.percentage) == str:
            self.percentage = Decimal(self.percentage.replace(".", "").replace(",", "."))
        if type(self.price_unit) == str:
            self.priceUnit = Decimal(self.price_unit.replace(".", "").replace(",", "."))


@dataclass
class CompanySupplement:
    cash_dividends: List[CashDividends]
    stock_dividends: List[StockDividends]
    subscriptions: List[Subscriptions]

    def __post_init__(self):
        self.cash_dividends = [CashDividends(**c) if type(c) == dict else c for c in self.cash_dividends]
        self.stock_dividends = [StockDividends(**c) if type(c) == dict else c for c in self.stock_dividends]
        self.subscriptions = [Subscriptions(**c) if type(c) == dict else c for c in self.subscriptions]


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


class RESTB3EventsClient:
    LATEST_EVENTS_URL = "https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0="
    STOCK_SUP_URL = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompany"
    BDR_SUP_URL = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompanyBDR"
    FII_SUP_URL = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedSupplementCompanyFunds"

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
            dump(asdict(request)).encode("utf-8")
        ), "utf-8")

    @staticmethod
    def parse_company_supplement(json: dict) -> CompanySupplement:
        # new_json = {to_snake_case(k): v for k, v in json.items()}
        tmp = snake_case_dict(json)

        return CompanySupplement(cash_dividends=tmp["cash_dividends"],
                                 stock_dividends=tmp["stock_dividends"],
                                 subscriptions=tmp["subscriptions"])


class ConfigurationClient:
    def __init__(self):
        self.client = boto3.client('ssm')

    def get_secret(self, key):
        resp = self.client.get_parameter(
            Name=key,
            WithDecryption=True
        )
        return resp['Parameter']['Value']


class TickerType(Enum):
    BDR = "BDR"
    FII = "FII"
    STOCK = "STOCK"


class RESTTickerInfoClient:
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


class DynamoCashDividendsRepository:
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("CashDividends")

    def save(self, event: CashDividendsEntity):
        self.__table.put_item(Item=event.to_dict())

    def batch_save(self, records: List[CashDividendsEntity]):
        # logger.debug(f"BatchSaving records: {records}")
        with self.__table.batch_writer() as batch:
            for record in records:
                batch.put_item(Item=record.to_dict())

    def find_by_payment_date(self, payment_date: datetime.date) -> List[CashDividendsEntity]:
        result = self.__table.query(
            IndexName="paymentDateAssetIssuedGlobalIndex",
            KeyConditionExpression=Key("payment_date").eq(payment_date.strftime("%Y%m%d"))
        )
        return list(map(lambda i: CashDividendsEntity(**i), result["Items"]))

events_client = RESTB3EventsClient()

# events_client.get_stock_supplement("TCNO")
#
# # print(CashDividends(**load('{"asset_issued": "BRALZRCTF006", "payment_date": "25/04/2022", "rate": 0.771556, "related_to": "Mar\u00e7o/2022", "approved_on": "14/04/2022", "isin_code": "BRALZRCTF006", "label": "RENDIMENTO", "last_date_prior": "14/04/2022", "remarks": ""}')).to_entity().id)
# # exit(1)
# cash_dividends_repository = DynamoCashDividendsRepository()
# with open("full_dividends.txt", "r") as fp:
#     dividends = []
#     for line in fp.readlines():
#         cash = CashDividends(**load(line))
#         dividends.append(cash)
#
#     import collections
#     print([item for item, count in collections.Counter([d.id for d in [c.to_entity() for c in dividends]]).items() if count > 1])
#     # cash_dividends_repository.batch_save([c.to_entity() for c in dividends])

# exit(0)

scan_kwargs = {}
items = []

while not done:
    if start_key:
        scan_kwargs["ExclusiveStartKey"] = start_key
    response = ticker_data.scan(**scan_kwargs)
    start_key = response.get("LastEvaluatedKey", None)
    done = start_key is None
    items += response.get("Items", [])

print(len(items))

codes = set([i["code"] for i in filter(lambda i: i.get("asset_type"), items)])

print(len(codes))
print(codes)

ticker_client = RESTTickerInfoClient()


failed = []

with open("full_dividends.txt", "w+") as fp:
    for count, code in enumerate(codes):
        print(f"Processing company: {count}-{code}")

        try:
            supplement = None
            _type = ticker_client.get_ticker_code_type(code)
            if _type == TickerType.STOCK:
                supplement = events_client.get_stock_supplement(code)
            elif _type == TickerType.FII:
                supplement = events_client.get_stock_supplement(code)
            elif _type == TickerType.BDR:
                supplement = events_client.get_stock_supplement(code)
            else:
                print("Unidentified company type", code)

            if supplement:
                # TODO process other types of dividends
                for c in supplement.cash_dividends:
                    fp.write(dump(c.to_dict()))
                    fp.write("\n")
                # print([dump(e.to_dict()) for e in supplement.cash_dividends])
                # cash_dividends_repository.batch_save(
                #     [c.to_entity() for c in supplement.cash_dividends])
        except Exception:
            # metrics.add_metric(name="GetCompanySupplementError", unit=MetricUnit.Count, value=1)
            print(f"Error fetching company supplement: {code}")
            failed.append(code)

print("FAILED:")
print(failed)

# https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetListedCashDividends/bGFuZ3VhZ2U6cHQtYnIgcGFnZU51bWJlcjoxIHBhZ2VTaXplOjIwIHRyYWRpbmdOYW1lOklUU0EK
# ['BSHY', 'AFCR', 'G2DI', 'JPSA', 'BFDL', 'IFID', 'IFIE', 'OMGE', 'FDES', 'DCVY', 'M2PR', 'NEXT', 'SAET', 'A1EE', 'I1FO', 'BPML', 'C1OO', 'EALT', 'FSRF', 'EQIN']