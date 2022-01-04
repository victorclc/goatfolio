from dataclasses import asdict
from datetime import datetime

from aws_lambda_powertools.metrics import MetricUnit
from dateutil.relativedelta import relativedelta

from adapters.outbound.dynamo_corporate_events_repository import DynamoCorporateEventsRepository
from adapters.outbound.rest_b3_fetch_events_client import RESTB3EventsClient
from adapters.outbound.rest_ticker_info_client import RESTTickerInfoClient
from application.enums.ticker_type import TickerType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from application.ports.fetch_events_client import FetchEventsClient
from application.ports.ticker_info_client import TickerInfoClient

from aws_lambda_powertools import Logger, Metrics

from application.ports.corporate_events_repository import CorporateEventsRepository

logger = Logger()
metrics = Metrics(namespace="CorporateEvents", service="TodayCorporateEvents")


def fetch_today_corporate_events(events_client: FetchEventsClient,
                                 ticker_client: TickerInfoClient,
                                 repository: CorporateEventsRepository):
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
                repository.batch_save(
                    [EarningsInAssetCorporateEvent.from_stock_dividends(e) for e in supplement.stock_dividends])
        except Exception:
            metrics.add_metric(name="GetCompanySupplementError", unit=MetricUnit.Count, value=1)
            logger.exception(f"Error fetching company supplement: {company}")


if __name__ == '__main__':
    events = RESTB3EventsClient()
    ticker_info = RESTTickerInfoClient()
    fetch_today_corporate_events(events, RESTTickerInfoClient(), DynamoCorporateEventsRepository())
