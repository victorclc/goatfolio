from decimal import Decimal


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
    def node_invested_value(self):
        return self.data.bought_value - self.data.sold_amount * self.average_price

    @property
    def realized_profit(self):
        return (self.gross_sold_value - self.invested_sold_value).quantize(Decimal('0.01'))

    @property
    def gross_amount(self):
        return self.amount * self.data.close_price


class PositionDoublyLinkedList:
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
