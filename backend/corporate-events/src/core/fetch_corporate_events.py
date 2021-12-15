from datetime import datetime

from adapters.outbound.rest_b3_fetch_events_client import RESTB3EventsClient
from application.enums.ticker_type import TickerType
from application.ports.fetch_events_client import FetchEventsClient
from application.ports.ticker_info_client import TickerInfoClient


def fetch_today_corporate_events(events_client: FetchEventsClient, ticker_client: TickerInfoClient):
    companies = events_client.fetch_companies_updates_from_date(datetime.now().date())

    print(events_client.get_stock_supplement("BIDI"))
    for company in companies:
        _type = ticker_client.get_ticker_code_type(company.ticker_code)

        if _type == TickerType.STOCK:
            pass
        elif _type == TickerType.FII:
            pass
        elif _type == TickerType.BDR:
            pass



if __name__ == '__main__':
    events = RESTB3EventsClient()
    fetch_today_corporate_events(events, None)

