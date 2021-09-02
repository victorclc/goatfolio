from itertools import groupby

from goatcommons.portfolio.models import StockPosition
from goatcommons.portfolio.wrappers import StockPositionWrapperLinkedList


def group_stock_position_per_month(stock_positions: [StockPosition]) -> [StockPosition]:
    grouped_positions = []
    for date, positions in groupby(stock_positions, key=lambda p: p.date.replace(day=1)):
        grouped = StockPosition(date)
        for position in positions:
            grouped = grouped + position
        grouped_positions.append(grouped)
    return grouped_positions


def create_stock_position_wrapper_list(stock_positions: [StockPosition]) -> StockPositionWrapperLinkedList:
    doubly = StockPositionWrapperLinkedList()
    for h in stock_positions:
        doubly.append(h)
    return doubly
