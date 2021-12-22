from application.exceptions.TickerNotFound import TickerNotFound
from application.ports.ticker_info_repository import TickerInfoRepository


def ticker_from_isin_code(isin_code: str, repo: TickerInfoRepository) -> str:
    ticker = repo.get_ticker_from_isin_code(isin_code)
    if not ticker:
        raise TickerNotFound(f"No ticker found for isin_code: {isin_code}")
    return ticker
