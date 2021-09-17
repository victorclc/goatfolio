from datetime import datetime, timezone
from decimal import Decimal
import json


class AWSEventUtils:
    @staticmethod
    def get_event_subject(event):
        try:
            return event["requestContext"]["authorizer"]["claims"]["sub"]
        except KeyError:
            return None

    @staticmethod
    def get_path_param(event, param_name):
        try:
            return event["pathParameters"][param_name]
        except KeyError:
            return None

    @staticmethod
    def get_query_param(event, param_name):
        try:
            return event["queryStringParameters"][param_name]
        except KeyError:
            return ""

    @staticmethod
    def get_query_params(event):
        try:
            return event["queryStringParameters"]
        except KeyError:
            return None


class JsonUtils:
    @staticmethod
    def dump(_dict):
        return json.dumps(_dict, cls=JsonUtils.CustomEncoder)

    @staticmethod
    def load(json_str):
        return json.loads(json_str, parse_float=Decimal)

    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, datetime):
                return int(obj.timestamp())

            return json.JSONEncoder.default(self, obj)


class DatetimeUtils:
    @staticmethod
    def month_first_day_datetime(_date: datetime):
        return datetime(_date.year, _date.month, 1, tzinfo=timezone.utc)

    @staticmethod
    def same_year_and_month(date1, date2):
        return date1.year == date2.year and date1.month == date2.month
