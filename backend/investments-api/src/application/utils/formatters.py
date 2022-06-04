import locale
from decimal import Decimal

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def format_brazilian_currency(value: Decimal) -> str:
    return f"R$ {locale.currency(value, grouping=True, symbol=False)}"
