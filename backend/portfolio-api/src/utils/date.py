import datetime


def current_month_start() -> datetime.date:
    return datetime.datetime.now().date().replace(day=1)


def is_on_same_year_and_month(date_1: datetime.date, date_2: datetime.date):
    return date_1.year == date_2.year and date_1.month == date_2.month
