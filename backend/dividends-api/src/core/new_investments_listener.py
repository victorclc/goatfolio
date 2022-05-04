from aws_lambda_powertools import Logger

from application.models.invesments import StockInvestment

logger = Logger()


def is_new_investment(new_investment, old_investment):
    return new_investment and not old_investment


def is_deletion_of_investment(new_investment, old_investment):
    return not new_investment and old_investment


def is_edit_of_investment(new_investment, old_investment):
    return new_investment and old_investment


def check_for_applicable_cash_dividend(subject: str, new_investment: StockInvestment, old_investment: StockInvestment):
    if is_edit_of_investment(new_investment, old_investment):
        if new_investment.ticker == old_investment.ticker \
                and new_investment.alias_ticker == old_investment.alias_ticker \
                and new_investment.date == old_investment.date \
                and new_investment.amount == old_investment.amount:
            logger.info("No dividend related info edited, nothing to do.")
            return
