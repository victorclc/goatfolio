from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.constants import colors, icons
from application.investment import Investment, StockInvestment, StockDividend
from application.models.extract_icon import ExtractIcon
from application.models.extract_item import ExtractItem
from application.models.paginated_extract_items_result import PaginatedExtractItemsResult
from application.operation_type import OperationType
from application.ports.outbound.investment_repository import InvestmentRepository
from application.utils import formatters

OPERATION_ICONS = {
    OperationType.BUY: ExtractIcon(code_point=icons.TRENDING_UP, color=colors.GREEN),
    OperationType.SELL: ExtractIcon(code_point=icons.TRENDING_DOWN, color=colors.RED),
    OperationType.SPLIT: ExtractIcon(code_point=icons.CALL_SPLIT, color=colors.BROWN),
    OperationType.INCORP_ADD: ExtractIcon(code_point=icons.CALL_SPLIT, color=colors.BROWN),
    OperationType.GROUP: ExtractIcon(code_point=icons.GROUP_WORK_OUTLINED, color=colors.BROWN),
    OperationType.INCORP_SUB: ExtractIcon(code_point=icons.GROUP_WORK_OUTLINED, color=colors.BROWN),
}
OPERATION_LABELS = {
    OperationType.BUY: "Compra",
    OperationType.SELL: "Venda",
    OperationType.SPLIT: "Desdobramento",
    OperationType.INCORP_ADD: "Incorporação",
    OperationType.GROUP: "Grupamento",
    OperationType.INCORP_SUB: "Incorporação",
}

STOCK_DIVIDEND_ICON = ExtractIcon(code_point=icons.ATTACH_MONEY, color=colors.GREEN)
STOCK_DIVIDEND_LABELS = {
    "RENDIMENTO": "Rendimento",
    "DIVIDENDO": "Dividendo",
    "JRS CAP PROPRIO": "JCP"
}

DEFAULT_ICON = ExtractIcon(code_point=icons.CLEAR, color=colors.BROWN)


@dataclass
class PaginationInfo:
    limit: Optional[int] = None,
    last_evaluated_id: Optional[str] = None,
    last_evaluated_date: Optional[datetime.date] = None,


def get_icon_for_investment(investment: Investment):
    if isinstance(investment, StockInvestment):
        return OPERATION_ICONS[investment.operation]
    if isinstance(investment, StockDividend):
        return STOCK_DIVIDEND_ICON
    return DEFAULT_ICON


def get_label_for_investment(investment: Investment):
    if isinstance(investment, StockInvestment):
        return OPERATION_LABELS[investment.operation]
    if isinstance(investment, StockDividend):
        return STOCK_DIVIDEND_LABELS.get(investment.label, default=investment.label)
    return ""


def get_value_for_investment(investment: Investment) -> str:
    if isinstance(investment, StockInvestment):
        if investment.operation in [OperationType.BUY, OperationType.SELL]:
            return formatters.format_brazilian_currency(investment.price * investment.amount)
        if investment.operation in [OperationType.INCORP_ADD, OperationType.SPLIT]:
            return f"+{investment.amount} unid."
        if investment.operation in [OperationType.INCORP_SUB, OperationType.GROUP]:
            return f"-{investment.amount} unid."
    if isinstance(investment, StockDividend):
        return formatters.format_brazilian_currency(investment.amount)


def get_additional_info_1(investment: Investment):
    if isinstance(investment, StockInvestment):
        return investment.broker
    return ""


def get_additional_info_2(investment: Investment):
    if isinstance(investment, StockInvestment):
        return f"({investment.amount} x {formatters.format_brazilian_currency(investment.price)})"
    return ""


def get_observation(investment: Investment):
    if isinstance(investment, StockInvestment) and investment.external_system == "CEI":
        return f"*Importado pelo CEI"
    return ""


def get_modifiable(investment: Investment):
    if isinstance(investment, StockInvestment) and investment.operation in [OperationType.BUY, OperationType.SELL]:
        return True
    return False


def get_paginated_extract_items(
        subject: str,
        ticker: Optional[str],
        pagination: PaginationInfo,
        repo: InvestmentRepository
):
    investments, new_last_evaluated_id, new_last_evaluated_date = repo.find_by_subject(
        subject,
        ticker,
        pagination.limit,
        pagination.last_evaluated_id,
        pagination.last_evaluated_date,
        False
    )

    extract_items = [
        ExtractItem(
            icon=get_icon_for_investment(i),
            label=get_label_for_investment(i),
            date=i.date,
            key=i.ticker,
            value=get_value_for_investment(i),
            additional_info_1=get_additional_info_1(i),
            additional_info_2=get_additional_info_2(i),
            observation=get_observation(i),
            modifiable=get_modifiable(i),
            investment=i
        )
        for i in investments
    ]

    return PaginatedExtractItemsResult(extract_items, new_last_evaluated_id, new_last_evaluated_date)
