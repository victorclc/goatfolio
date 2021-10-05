import datetime
import logging
import re
from io import StringIO
from typing import List, Tuple, Dict

import requests
import pandas as pd

from event_notifier.models import NotifyLevel
from goatcommons.utils.decorators import retry

from domain.ports.outbound.corporate_events_file_storage import (
    CorporateEventsFileStorage,
)
from domain.ports.outbound.corporate_events_repository import CorporateEventsRepository
import event_notifier.decorators as notifier
from domain.models.earnings_in_assets_event import EarningsInAssetCorporateEvent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class B3CorporateEventsCrawler:
    def __init__(self, storage: CorporateEventsFileStorage):
        self.storage = storage

    @notifier.notify("Successful Count: {}\nFailed URLs: {}", NotifyLevel.INFO)
    def craw_corporate_events_from_date(self, date: datetime.date):
        failed_urls = []
        success_count = 0
        for cvm_code, url in self.get_updated_company_links(date):
            try:
                if "fundsPage" in url:
                    self.handle_fund_page(cvm_code, url, date)
                else:
                    self.handle_normal_page(cvm_code, url, date)
                success_count += 1
            except Exception:  # TODO check what is the exception throwed here
                failed_urls.append(url)
        return success_count, failed_urls

    def handle_fund_page(self, cvm_code: str, url: str, date: datetime.date):
        # TODO
        return

    @retry(Exception, tries=3, delay=0.1, logger=logger)
    def handle_normal_page(self, cvm_code: str, url: str, date: datetime.date):
        tables = pd.read_html(url)
        count = 0
        for table in tables:
            csv_name = f'{cvm_code}-{date.strftime("%Y%m%d")}-{count}.csv'
            csv_buffer = StringIO()
            table.to_csv(csv_buffer)
            self.storage.upload(csv_buffer, csv_name)
            count = count + 1

    def get_updated_company_links(self, date: datetime.date) -> List[Tuple[str, str]]:
        events = self.get_last_seven_days_corporate_events()

        return [
            (e["codeCvm"], re.sub(r"en-US$", "pt-BR", e["url"]))
            for e in self.filter_corporate_events_by_date(events, date)
        ]

    @staticmethod
    def get_last_seven_days_corporate_events():
        url = "https://sistemaswebb3-listados.b3.com.br/dividensOtherCorpActProxy/DivOtherCorpActCall/GetListDivOtherCorpActions/eyJsYW5ndWFnZSI6InB0LWJyIn0="
        data = requests.get(url, verify=False).json()
        logger.info(f"b3 corporate events response: {data}")
        return data

    @staticmethod
    def filter_corporate_events_by_date(events: List, date: datetime.date):
        filtered_data = list(
            filter(lambda i: i["date"] == date.strftime("%d/%m/%Y"), events)
        )
        if not filtered_data:
            logger.info("filtering by alternative date format")
            filtered_data = list(
                filter(
                    lambda i: i["date"] == date.strftime("%m/%d/%Y"),
                    events,
                )
            )
        return filtered_data[0]['results']


class B3CorporateEventsFileProcessor:
    def __init__(
        self, storage: CorporateEventsFileStorage, repository: CorporateEventsRepository
    ):
        self.storage = storage
        self.repository = repository

    def process_corporate_events_file(self, file_name: str):
        downloaded_path = self.storage.download(file_name)
        table = pd.read_csv(downloaded_path)

        if self.is_earnings_in_assets(table.columns):
            logger.info(f"Procesing earnings in asset type file: {file_name}.")
            self.standardize_table_columns(table)
            records = table.to_dict("records")
            self.repository.batch_save(self.parse_to_earnings_in_asset(records))
            self.storage.move_to_archive(file_name)
        else:
            self.storage.move_to_unprocessed(file_name)

    @staticmethod
    def parse_to_earnings_in_asset(
        records: List[Dict],
    ) -> List[EarningsInAssetCorporateEvent]:
        for record in records:
            record["with_date"] = datetime.datetime.strptime(
                record["with_date"], "%d/%m/%Y"
            ).strftime("%Y%m%d")
            record["deliberate_on"] = datetime.datetime.strptime(
                record["deliberate_on"], "%d/%m/%Y"
            ).strftime("%Y%m%d")
        return [EarningsInAssetCorporateEvent(**row) for row in records]

    @staticmethod
    def standardize_table_columns(table):
        table.drop("Unnamed: 0", inplace=True, axis=1)
        table.columns = [
            "type",
            "isin_code",
            "deliberate_on",
            "with_date",
            "grouping_factor",
            "emitted_asset",
            "observations",
        ]

    @staticmethod
    def is_earnings_in_assets(columns: List) -> bool:
        return set(columns) == {
            "Unnamed: 0",
            "Proventos",
            "Código ISIN",
            "Deliberado em",
            "Negócios com até",
            "% / Fator de Grupamento",
            "Ativo Emitido",
            "Observações",
        }
