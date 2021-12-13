from application.ports.ticker_info_repository import TickerInfoRepository


def ticker_exists(ticker: str, repo: TickerInfoRepository) -> bool:
    code = repo.get_isin_code_from_ticker(ticker)
    return code is not None
