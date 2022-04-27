from typing import List, Protocol

from adapters.outbound.dynamo_corporate_events_repository import DynamoCorporateEventsRepository
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent


class CorporateEventsRepository(Protocol):
    def find_by_emitted_asset(self, emitted_isin: str) -> List[EarningsInAssetCorporateEvent]:
        ...


def get_all_previous_symbols(isin_code: str, corp_events_repository: CorporateEventsRepository) -> List[str]:
    previous_symbols = []
    events = corp_events_repository.find_by_emitted_asset(isin_code)
    for event in events:
        previous_symbols.append(event.isin_code)
        previous_symbols += get_all_previous_symbols(event.isin_code, corp_events_repository)

    return previous_symbols


if __name__ == '__main__':
    print(get_all_previous_symbols("BRAESBACNOR7", DynamoCorporateEventsRepository()))