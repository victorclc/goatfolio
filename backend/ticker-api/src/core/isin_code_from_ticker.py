from application.exceptions.IsinNotFound import IsinNotFound
from application.ports.ticker_info_repository import TickerInfoRepository


def isin_code_from_ticker(ticker: str, repo: TickerInfoRepository) -> str:
    isin = repo.get_isin_code_from_ticker(ticker)
    if not isin:
        raise IsinNotFound(f"No isin_code found for ticker: {ticker}")
    return isin
