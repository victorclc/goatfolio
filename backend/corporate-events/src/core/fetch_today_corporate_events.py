from dataclasses import asdict
from datetime import datetime
from typing import Protocol, List

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit

from adapters.outbound.dynamo_cash_dividends_repository import DynamoCashDividendsRepository
from adapters.outbound.dynamo_corporate_events_repository import DynamoCorporateEventsRepository
from adapters.outbound.rest_b3_fetch_events_client import RESTB3EventsClient
from adapters.outbound.rest_ticker_info_client import RESTTickerInfoClient
from application.entities.cash_dividends import CashDividendsEntity
from application.enums.ticker_type import TickerType
from application.models.companies_updates import CashDividends
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from application.ports.corporate_events_repository import CorporateEventsRepository
from application.ports.fetch_events_client import FetchEventsClient
from application.ports.ticker_info_client import TickerInfoClient

logger = Logger()
metrics = Metrics(namespace="CorporateEvents", service="TodayCorporateEvents")


class StockDividendsRepository(Protocol):
    def batch_save(self, records: List[EarningsInAssetCorporateEvent]):
        ...


class CashDividendsRepository(Protocol):
    def batch_save(self, records: List[CashDividendsEntity]):
        ...


def fetch_today_corporate_events(events_client: FetchEventsClient,
                                 ticker_client: TickerInfoClient,
                                 stock_dividends_repository: CorporateEventsRepository,
                                 cash_dividends_repository: CashDividendsRepository):
    companies = events_client.fetch_companies_updates_from_date(datetime.now().date())

    metrics.add_metric(name="TotalUpdatedCompanies", unit=MetricUnit.Count, value=len(companies))

    for company in companies:
        logger.info(f"Processing company: {company}")

        try:
            supplement = None
            _type = ticker_client.get_ticker_code_type(company.ticker_code)
            if _type == TickerType.STOCK:
                supplement = events_client.get_stock_supplement(company.ticker_code)
            elif _type == TickerType.FII:
                supplement = events_client.get_stock_supplement(company.ticker_code)
            elif _type == TickerType.BDR:
                supplement = events_client.get_stock_supplement(company.ticker_code)
            else:
                metrics.add_metric(name="UnidentifiedCompanyType", unit=MetricUnit.Count, value=1)
                logger.warning("Unidentified company type", extra=asdict(company))

            if supplement:
                # TODO process other types of dividends
                metrics.add_metric(name="GetCompanySupplementSuccess", unit=MetricUnit.Count, value=1)
                stock_dividends_repository.batch_save(
                    [EarningsInAssetCorporateEvent.from_stock_dividends(e) for e in supplement.stock_dividends])
                cash_dividends_repository.batch_save(
                    cash_dividends_entity_mapper(supplement.cash_dividends)
                )
        except Exception:
            metrics.add_metric(name="GetCompanySupplementError", unit=MetricUnit.Count, value=1)
            logger.exception(f"Error fetching company supplement: {company}")


def cash_dividends_entity_mapper(cash_dividends: List[CashDividends]):
    _entities = []
    ids = {}
    for dividend in cash_dividends:
        entity = dividend.to_entity()
        if entity.id in ids:
            new_id = entity.id + str(ids[entity.id])
            ids[entity.id] += 1
            entity.id = new_id
        else:
            ids[entity.id] = 0
        _entities.append(entity)
    return _entities


if __name__ == '__main__':
    events = RESTB3EventsClient()
    ticker_info = RESTTickerInfoClient()
    fetch_today_corporate_events(
        events,
        RESTTickerInfoClient(),
        DynamoCorporateEventsRepository(),
        DynamoCashDividendsRepository()
    )
