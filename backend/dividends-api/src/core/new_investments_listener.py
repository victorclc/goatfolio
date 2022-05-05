from datetime import datetime
from typing import Protocol, List, Set

from aws_lambda_powertools import Logger

from adapters.outbound.dynamo_investments_repository import DynamoInvestmentRepository
from application.models.dividends import CashDividends
from application.models.invesments import StockInvestment, StockDividend
from core.helpers import CashDividendsEarningsHelper, CorporateEventsClient, TickerInfoClient

logger = Logger()


class CashDividendsClient(Protocol):
    def get_cash_dividends_for_ticker(
            self, ticker: str, from_date: datetime.date
    ) -> List[CashDividends]:
        ...


def is_new_investment(new_investment, old_investment):
    return new_investment and not old_investment


def is_deletion_of_investment(new_investment, old_investment):
    return not new_investment and old_investment


def is_edit_of_investment(new_investment, old_investment):
    return new_investment and old_investment


def get_tickers_set(new_investment, old_investment) -> Set:
    tickers = set()
    if new_investment:
        tickers.add(new_investment.ticker)
    if old_investment:
        tickers.add(old_investment.ticker)
    return tickers


def check_for_applicable_cash_dividend(
        subject: str,
        new_investment: StockInvestment,
        old_investment: StockInvestment,
        dividends_client: CashDividendsClient,
        corporate_events_client: CorporateEventsClient,
        ticker_info_client: TickerInfoClient,
        investments_repository: DynamoInvestmentRepository,
):
    if is_edit_of_investment(new_investment, old_investment):
        if new_investment.ticker == old_investment.ticker \
                and new_investment.alias_ticker == old_investment.alias_ticker \
                and new_investment.date == old_investment.date \
                and new_investment.amount == old_investment.amount:
            logger.info("No dividend related info edited, nothing to do.")
            return
    else:
        # ANALISAR ESSE PROCESSO, COMO VAMOS ATUALIZAR UM DIVIDENDO Q JA EXISTE? NO CASO DE DELETAR POR EXEMPLO? TALVEZ
        if new_investment:
            investment = new_investment
        else:
            investment = old_investment

        dividends = filter(
            lambda c: c.payment_date <= datetime.now().date(),
            dividends_client.get_cash_dividends_for_ticker(investment.ticker, investment.date)
        )

        helper = CashDividendsEarningsHelper(corporate_events_client, ticker_info_client, investments_repository)
        payouts = []
        for dividend in dividends:
            ticker, earnings = helper.calculate_earnings_of_cash_dividend_for_subject(subject, dividend)
            if earnings > 0:
                _id = f"STOCK_DIVIDEND#{ticker}#{dividend.id}"
                payouts.append(StockDividend(ticker, dividend.label, earnings, subject, dividend.payment_date, _id))

        if payouts:
            ...  # BATCH_SAVE
