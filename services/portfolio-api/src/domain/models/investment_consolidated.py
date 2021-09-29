from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from decimal import Decimal
from itertools import groupby
from typing import List, Optional

from dateutil.relativedelta import relativedelta

from domain.models.investment import StockInvestment
from domain.models.investment_position import InvestmentPosition, StockPosition
from domain.models.investment_position_summary import StockPositionSummary
from domain.models.investment_summary import InvestmentSummary, StockSummary
from domain.models.portfolio_item import PortfolioItem

DATE_FORMAT = "%Y%m%d"


@dataclass
class InvestmentConsolidated(PortfolioItem, ABC):
    initial_date: dt.date = dt.datetime.max.date()
    history: List[InvestmentPosition] = field(default_factory=list)
    alias_ticker: str = field(default="")

    def __post_init__(self):
        if not isinstance(self.initial_date, dt.date):
            self.initial_date = dt.datetime.strptime(
                str(self.initial_date), DATE_FORMAT
            ).date()

    def to_dict(self) -> dict:
        ret = {
            **self.__dict__,
            "initial_date": self.initial_date.strftime(DATE_FORMAT),
            "history": sorted(
                [h.to_dict() for h in self.history], key=lambda h: h["date"]
            ),
            "alias_ticker": self.alias_ticker or self.ticker,
        }
        return ret

    def current_ticker_name(self):
        return self.alias_ticker or self.ticker

    @abstractmethod
    def add_investment(self, investment):
        """Adds the investment"""

    def export_investment_summary(self) -> Optional[InvestmentSummary]:
        """Creates an InvestmentSummary objects based on history"""


class StockPositionWrapper:
    def __init__(self, data: StockPosition):
        self.data = data
        self.next: Optional[StockPositionWrapper] = None
        self.prev: Optional[StockPositionWrapper] = None

    @property
    def date(self) -> dt.date:
        return self.data.date

    @property
    def amount(self):
        if self.prev:
            return self.prev.amount + self.data.bought_amount - self.data.sold_amount
        return self.data.bought_amount - self.data.sold_amount

    @property
    def bought_amount(self):
        if self.prev and self.prev.amount > 0:
            return self.prev.bought_amount + self.data.bought_amount
        return self.data.bought_amount

    @property
    def bought_value(self):
        if self.prev and self.prev.amount > 0:
            return self.prev.bought_value + self.data.bought_value
        return self.data.bought_value

    @property
    def average_price(self):
        bought_amount = self.bought_amount
        if bought_amount > 0:
            return (self.bought_value / bought_amount).quantize(Decimal("0.01"))
        return 0

    @property
    def gross_sold_value(self):
        if self.prev:
            return self.prev.position_sold_value + self.data.sold_value
        return self.data.sold_value

    @property
    def invested_sold_value(self):
        if self.prev:
            return (
                self.prev.current_invested_sold_value
                + self.data.sold_amount * self.average_price
            )
        return self.data.sold_amount * self.average_price

    @property
    def current_invested_sold_value(self):
        if self.prev and self.prev.amount > 0:
            return (
                self.prev.current_invested_sold_value
                + self.data.sold_amount * self.average_price
            )
        return self.data.sold_amount * self.average_price

    @property
    def current_invested_value(self):
        if self.prev:
            return (self.bought_value - self.current_invested_sold_value).quantize(
                Decimal("0.01")
            )
        return (self.data.bought_value - self.current_invested_sold_value).quantize(
            Decimal("0.01")
        )

    @property
    def node_invested_value(self):
        return self.data.bought_value - self.data.sold_amount * self.average_price

    @property
    def node_invested_sold_value(self):
        return self.data.sold_amount * self.average_price

    @property
    def realized_profit(self):
        return (self.gross_sold_value - self.invested_sold_value).quantize(
            Decimal("0.01")
        )

    @property
    def gross_value(self):
        return self.amount * self.data.close_price

    @property
    def prev_adjusted_gross_value(self):
        if self.prev and self.prev.amount > 0:
            if self.data.sold_amount > 0:
                prev_month_amount = self.prev.amount - round(
                    self.node_invested_sold_value / self.prev.average_price
                )
            else:
                prev_month_amount = self.prev.amount
            return prev_month_amount * self.prev.data.close_price
        return 0

    @property
    def month_variation_percent(self):
        if self.prev and self.prev.amount > 0:
            prev_gross_value = self.prev_adjusted_gross_value + self.data.bought_value
        else:
            prev_gross_value = self.current_invested_value
        if prev_gross_value > 0:
            return ((self.gross_value * 100 / prev_gross_value) - 100).quantize(
                Decimal("0.01")
            )
        return 0


class StockPositionWrapperLinkedList:
    def __init__(self):
        self.head: Optional[StockPositionWrapper] = None
        self.tail: Optional[StockPositionWrapper] = None
        self._current: Optional[StockPositionWrapper] = None
        self._first_interaction = False

    def __iter__(self):
        self._first_interaction = True
        self._current = self.head
        return self

    def __next__(self) -> StockPositionWrapper:
        if not self._current:
            raise StopIteration
        if self._first_interaction:
            self._first_interaction = False
            return self._current
        self._current = self._current.next
        if not self._current:
            raise StopIteration
        return self._current

    def push(self, new_val: StockPosition):
        new_node = StockPositionWrapper(new_val)
        new_node.next = self.head
        if self.head is not None:
            self.head.prev = new_node
        self.head = new_node

    def insert(self, prev_node, new_val):
        if prev_node is None:
            return
        new_node = StockPositionWrapper(new_val)
        new_node.next = prev_node.next
        prev_node.next = new_node
        new_node.prev = prev_node
        if new_node.next:
            new_node.next.prev = new_node
        else:
            self.tail = new_node

    def append(self, new_val):
        new_node = StockPositionWrapper(new_val)
        new_node.next = None

        if self.head is None:
            new_node.prev = None
            self.head = new_node
            self.tail = new_node
            return

        last = self.head
        while last.next:
            last = last.next
        last.next = new_node
        new_node.prev = last
        self.tail = new_node

    def find(self, func):
        curr = self.head
        while curr:
            if func(curr):
                return curr
            curr = curr.next
        return None

    @staticmethod
    def list_print(node):
        while node:
            print(node.data),
            node = node.next


@dataclass
class StockConsolidated(InvestmentConsolidated):
    def __post_init__(self):
        super().__post_init__()
        self.history = [
            StockPosition(**h) if isinstance(h, dict) else h for h in self.history
        ]

    def __add__(self, other):
        initial_date = min(self.initial_date, other.initial_date)
        return StockConsolidated(
            self.subject,
            self.alias_ticker or self.ticker,
            initial_date=initial_date,
            history=self.history + other.history,
        )

    def find_position_in_history(self, date: dt.date) -> Optional[StockPosition]:
        return next(
            (position for position in self.history if position.date == date),
            None,
        )

    def create_empty_position(self, date: dt.date) -> StockPosition:
        p = StockPosition(date)
        self.history.append(p)
        return p

    def add_investment(self, investment: StockInvestment):
        self.initial_date = min(self.initial_date, investment.date)
        if investment.alias_ticker:
            self.alias_ticker = investment.alias_ticker

        position = self.find_position_in_history(investment.date)
        if not position:
            position = self.create_empty_position(investment.date)

        position.add_investment(investment)
        if position.is_empty():
            self.history.remove(position)

    def export_investment_summary(self) -> Optional[StockSummary]:
        wrapper = self.monthly_stock_position_wrapper_linked_list()
        if not wrapper.tail:
            return

        current = wrapper.tail
        previous = current.prev

        previous_position = None
        latest_position = StockPositionSummary(
            date=current.data.date,
            amount=current.amount,
            invested_value=current.current_invested_value,
            bought_value=current.data.bought_value,
            average_price=current.average_price,
        )
        if previous:
            previous_position = StockPositionSummary(
                date=previous.data.date, amount=previous.amount
            )

        return StockSummary(
            self.ticker,
            alias_ticker=self.alias_ticker,
            latest_position=latest_position,
            previous_position=previous_position,
        )

    def grouped_by_month_stock_position(self) -> List[StockPosition]:
        grouped_positions = []
        for date, positions in groupby(
            sorted(self.history, key=lambda h: h.date),
            key=lambda p: p.date.replace(day=1),
        ):
            grouped = StockPosition(date)
            for position in positions:
                grouped = grouped + position
            grouped_positions.append(grouped)
        return grouped_positions

    def monthly_stock_position_wrapper_linked_list(
        self,
        to_date: dt.date = None,
    ) -> StockPositionWrapperLinkedList:
        doubly = StockPositionWrapperLinkedList()

        prev_date = self.initial_date.replace(day=1)
        for h in self.grouped_by_month_stock_position():
            if h.date > prev_date + relativedelta(months=1):
                while prev_date < h.date:  # filling the gaps
                    doubly.append(StockPosition(prev_date))
                    prev_date += relativedelta(months=1)
            doubly.append(h)

        if to_date and doubly.tail:
            while doubly.tail.date < to_date:
                doubly.append(StockPosition(prev_date))
                prev_date += relativedelta(months=1)

        return doubly
