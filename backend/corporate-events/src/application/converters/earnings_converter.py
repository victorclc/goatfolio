from application.models.earnings_in_assets_event import ManualEarningsInAssetCorporateEvents, \
    EarningsInAssetCorporateEvent
from application.ports.ticker_info_client import TickerInfoClient


def manual_earning_to_earnings_in_assets_converter(earning: ManualEarningsInAssetCorporateEvents,
                                                   client: TickerInfoClient) -> EarningsInAssetCorporateEvent:
    return EarningsInAssetCorporateEvent(
        type=earning.type,
        isin_code=client.get_isin_code_from_ticker(earning.ticker),
        deliberate_on=earning.last_date_prior,
        with_date=earning.last_date_prior,
        grouping_factor=earning.grouping_factor,
        emitted_asset=client.get_isin_code_from_ticker(earning.emitted_ticker),
        observations="",
        id=earning.id,
        emitted_ticker=earning.emitted_ticker,
        subject=earning.subject)
