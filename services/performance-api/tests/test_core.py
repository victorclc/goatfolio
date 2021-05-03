import unittest

from core import PerformanceCore


class TestPerformanceCore(unittest.TestCase):
    def setUp(self):
        self.core = PerformanceCore()

    # add multiple investment in different dates, must create multiple amount of StockPosition
    def test_somehing(self):
        self.assertTrue(True)
