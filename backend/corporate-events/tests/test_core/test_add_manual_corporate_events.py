import datetime
import unittest
from decimal import Decimal
from unittest.mock import MagicMock

from dateutil.relativedelta import relativedelta

from application.exceptions.validation_errors import InvalidEmittedTickerError, InvalidLastDatePriorError, \
    InvalidGroupingFactorError
from application.models.manual_event import IncorporationEvent, GroupEvent, SplitEvent
from core import add_manual_corporate_events as manual


def tomorrow() -> datetime.date:
    return (datetime.datetime.now() + relativedelta(days=1)).date()


class TestAddIncorporationCorporateEvent(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = MagicMock()
        self.repo.save = MagicMock()
        self.ticker_client = MagicMock()
        self.ticker_client.is_ticker_valid = MagicMock(return_value=True)
        self.subject = "1111-2222-3333-4444"

    def test_add_event_with_invalid_emitted_ticker(self):
        event = IncorporationEvent(ticker="BIDI11",
                                   emitted_ticker="SEILA11",
                                   grouping_factor=Decimal(2),
                                   last_date_prior=datetime.date(2022, 1, 1))
        self.ticker_client.is_ticker_valid = MagicMock(return_value=False)

        with self.assertRaises(InvalidEmittedTickerError):
            manual.add_incorporation_corporate_event(subject=self.subject,
                                                     incorporation=event,
                                                     repo=self.repo,
                                                     ticker_client=self.ticker_client)
        self.repo.save.assert_not_called()

    def test_add_event_with_invalid_last_date_prior(self):
        event = IncorporationEvent(ticker="VVAR3",
                                   emitted_ticker="VIIA3",
                                   grouping_factor=Decimal(2),
                                   last_date_prior=tomorrow())

        with self.assertRaises(InvalidLastDatePriorError):
            manual.add_incorporation_corporate_event(subject=self.subject,
                                                     incorporation=event,
                                                     repo=self.repo,
                                                     ticker_client=self.ticker_client)
        self.repo.save.assert_not_called()

    def test_add_valid_event(self):
        event = IncorporationEvent(ticker="VVAR3",
                                   emitted_ticker="VIIA3",
                                   grouping_factor=Decimal(2),
                                   last_date_prior=datetime.date(2021, 7, 1))

        manual.add_incorporation_corporate_event(subject=self.subject,
                                                 incorporation=event,
                                                 repo=self.repo,
                                                 ticker_client=self.ticker_client)
        self.repo.save.asset_called_once()


class TestAddGroupCorporateEvent(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = MagicMock()
        self.repo.save = MagicMock()
        self.subject = "1111-2222-3333-4444"

    def test_add_event_with_grouping_factor_equal_1(self):
        event = GroupEvent(ticker="BIDI11",
                           grouping_factor=Decimal(1),
                           last_date_prior=datetime.date(2022, 1, 1))

        with self.assertRaises(InvalidGroupingFactorError):
            manual.add_group_corporate_event(subject=self.subject,
                                             group=event,
                                             repo=self.repo)
        self.repo.save.assert_not_called()

    def test_add_event_with_grouping_factor_greater_than_1(self):
        event = GroupEvent(ticker="BIDI11",
                           grouping_factor=Decimal(2),
                           last_date_prior=datetime.date(2022, 1, 1))

        with self.assertRaises(InvalidGroupingFactorError):
            manual.add_group_corporate_event(subject=self.subject,
                                             group=event,
                                             repo=self.repo)
        self.repo.save.assert_not_called()

    def test_add_event_with_grouping_factor_less_than_1(self):
        event = GroupEvent(ticker="BIDI11",
                           grouping_factor=Decimal(0.5),
                           last_date_prior=datetime.date(2022, 1, 1))

        manual.add_group_corporate_event(subject=self.subject,
                                         group=event,
                                         repo=self.repo)
        self.repo.save.assert_called_once()

    def test_add_event_with_invalid_last_date_prior(self):
        event = GroupEvent(ticker="BIDI11",
                           grouping_factor=Decimal(0.5),
                           last_date_prior=tomorrow())

        with self.assertRaises(InvalidLastDatePriorError):
            manual.add_group_corporate_event(subject=self.subject,
                                             group=event,
                                             repo=self.repo)
        self.repo.save.assert_not_called()


class TestAddSplitCorporateEvent(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = MagicMock()
        self.repo.save = MagicMock()
        self.subject = "1111-2222-3333-4444"

    def test_add_event_with_grouping_factor_equal_1(self):
        event = SplitEvent(ticker="BIDI11",
                           grouping_factor=Decimal(1),
                           last_date_prior=datetime.date(2022, 1, 1))

        with self.assertRaises(InvalidGroupingFactorError):
            manual.add_split_corporate_event(subject=self.subject,
                                             split=event,
                                             repo=self.repo)
        self.repo.save.assert_not_called()

    def test_add_event_with_grouping_factor_less_than_1(self):
        event = SplitEvent(ticker="BIDI11",
                           grouping_factor=Decimal(0.5),
                           last_date_prior=datetime.date(2022, 1, 1))

        with self.assertRaises(InvalidGroupingFactorError):
            manual.add_split_corporate_event(subject=self.subject,
                                             split=event,
                                             repo=self.repo)
        self.repo.save.assert_not_called()

    def test_add_event_with_grouping_factor_greater_than_1(self):
        event = SplitEvent(ticker="BIDI11",
                           grouping_factor=Decimal(2),
                           last_date_prior=datetime.date(2022, 1, 1))

        manual.add_split_corporate_event(subject=self.subject,
                                         split=event,
                                         repo=self.repo)
        self.repo.save.assert_called_once()

    def test_add_event_with_invalid_last_date_prior(self):
        event = SplitEvent(ticker="BIDI11",
                           grouping_factor=Decimal(2),
                           last_date_prior=tomorrow())

        with self.assertRaises(InvalidLastDatePriorError):
            manual.add_split_corporate_event(subject=self.subject,
                                             split=event,
                                             repo=self.repo)
        self.repo.save.assert_not_called()
