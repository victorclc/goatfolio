from typing import Optional

from application.enums.ticker_type import TickerType
from application.ports.ticker_info_repository import TickerInfoRepository


def ticker_code_type(
    ticker_code: str, repo: TickerInfoRepository
) -> Optional[TickerType]:
    infos = repo.find_by_code(ticker_code)
    for info in infos:
        if info.asset_type:
            return info.asset_type
