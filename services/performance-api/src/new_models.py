from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment


@dataclass
class StockPosition:
    date: datetime
    sold_amount: Decimal
    bought_amount: Decimal
    bought_value: Decimal
    sold_value: Decimal

    def __post_init__(self):
        if type(self.date) is not datetime:
            self.date = datetime.fromtimestamp(self.date, tz=timezone.utc)

        self.sold_amount = Decimal(self.sold_amount).quantize(Decimal('0.01'))
        self.bought_amount = Decimal(self.bought_amount).quantize(Decimal('0.01'))
        self.bought_value = Decimal(self.bought_value).quantize(Decimal('0.01'))
        self.sold_value = Decimal(self.sold_value).quantize(Decimal('0.01'))

    def __add__(self, other):
        sold_amount = self.sold_amount + other.sold_amount
        bought_amount = self.bought_amount + other.bought_amount
        bought_value = self.bought_value + other.bought_value
        sold_value = self.sold_value + other.sold_value

        return StockPosition(self.date, sold_amount, bought_amount, bought_value, sold_value)

    @staticmethod
    def from_stock_investment(investment: StockInvestment):
        sold_amount = 0
        sold_value = 0
        bought_amount = 0
        bought_value = 0
        date = investment.date

        if investment.operation == OperationType.BUY:
            bought_amount = investment.amount
            bought_value = investment.amount * investment.price
        elif investment.operation == OperationType.SELL:
            sold_amount = investment.amount
            sold_value = investment.amount * investment.price
        elif investment.operation in [OperationType.SPLIT, OperationType.INCORP_ADD]:
            bought_amount = investment.amount
        elif investment.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            sold_amount = investment.amount
        return StockPosition(date, sold_amount, bought_amount, bought_value, sold_value)

    def add_investment(self, investment):
        sold_amount = 0
        sold_value = 0
        bought_amount = 0
        bought_value = 0

        if investment.operation == OperationType.BUY:
            bought_amount = investment.amount
            bought_value = investment.amount * investment.price
        elif investment.operation == OperationType.SELL:
            sold_amount = investment.amount
            sold_value = investment.amount * investment.price
        elif investment.operation in [OperationType.SPLIT, OperationType.INCORP_ADD]:
            bought_amount = investment.amount
        elif investment.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            sold_amount = investment.amount

        self.sold_amount = self.sold_amount + sold_amount
        self.sold_value = self.sold_value + sold_value
        self.bought_amount = self.bought_amount + bought_amount
        self.bought_value = self.bought_value + bought_value

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


class StockPositionWrapper:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

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
            return (self.bought_value / bought_amount).quantize(Decimal('0.01'))
        return 0

    @property
    def gross_sold_value(self):
        if self.prev:
            return self.prev.position_sold_value + self.data.sold_value
        return self.data.sold_value

    @property
    def invested_sold_value(self):
        if self.prev:
            return self.prev.current_invested_sold_value + self.data.sold_amount * self.average_price
        return self.data.sold_amount * self.average_price

    @property
    def current_invested_sold_value(self):
        if self.prev and self.prev.amount > 0:
            return self.prev.current_invested_sold_value + self.data.sold_amount * self.average_price
        return self.data.sold_amount * self.average_price

    @property
    def current_invested_value(self):
        if self.prev:
            return (self.bought_value - self.current_invested_sold_value).quantize(Decimal('0.01'))
        return (self.data.bought_value - self.current_invested_sold_value).quantize(Decimal('0.01'))

    @property
    def realized_profit(self):
        return (self.gross_sold_value - self.invested_sold_value).quantize(Decimal('0.01'))


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, new_val):

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


if __name__ == '__main__':
    p1 = StockPosition(datetime(2020, 2, 27), 0, Decimal(10), Decimal(10 * 52.26), sold_value=0)
    p2 = StockPosition(datetime(2020, 3, 5), 0, Decimal(10), Decimal(10 * 49.05), sold_value=0)
    p3 = StockPosition(datetime(2020, 3, 6), 0, Decimal(5), Decimal(5 * 44.07), sold_value=0)
    p4 = StockPosition(datetime(2020, 3, 9), 0, Decimal(10), Decimal(10 * 39.68), sold_value=0)
    p5 = StockPosition(datetime(2020, 3, 12), 0, Decimal(5), Decimal(5 * 31.54), sold_value=0)
    p6 = StockPosition(datetime(2020, 3, 12), 0, Decimal(10), Decimal(10 * 34.32), sold_value=0)
    p7 = StockPosition(datetime(2020, 3, 18), 0, Decimal(15), Decimal(15 * 33.13), sold_value=0)
    p8 = StockPosition(datetime(2020, 10, 9), 0, Decimal(32), Decimal(32 * 95.70), sold_value=0)
    p9 = StockPosition(datetime(2020, 10, 9), 0, Decimal(10), Decimal(10 * 95.70), sold_value=0)
    p10 = StockPosition(datetime(2020, 2, 27), 0, Decimal(321), Decimal(0), sold_value=0)

    doubly = DoublyLinkedList()
    doubly.append(p1)
    doubly.append(p2)
    doubly.append(p3)
    doubly.append(p4)
    doubly.append(p5)
    doubly.append(p6)
    doubly.append(p7)
    doubly.append(p8)
    doubly.append(p9)
    doubly.append(p10)

    x = StockPosition
    print(x)

    print(doubly.tail.current_invested_value)
