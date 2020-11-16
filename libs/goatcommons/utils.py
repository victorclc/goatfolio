from decimal import Decimal
import json

from goatcommons.constants import InvestmentsType
from goatcommons.models import StockInvestment, PreFixedInvestment, PostFixedInvestment, CheckingAccountInvestment


class AwsEventUtils:
    @staticmethod
    def get_event_subject(event):
        try:
            return event['requestContext']['authorizer']['claims']['sub']
        except KeyError:
            return None

    @staticmethod
    def get_path_param(event, param_name):
        try:
            return event['pathParameters'][param_name]
        except KeyError:
            return None


class JsonUtils:
    @staticmethod
    def dump(_dict):
        return json.dumps(_dict, cls=JsonUtils.DecimalEncoder)

    @staticmethod
    def load(json_str):
        return json.loads(json_str, parse_float=Decimal)

    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return json.JSONEncoder.default(self, obj)


class InvestmentUtils:
    @staticmethod
    def load_model_by_type(_type, investment):
        if _type == InvestmentsType.STOCK:
            return StockInvestment(**investment, type=InvestmentsType.STOCK)
        if _type == InvestmentsType.PRE_FIXED:
            return PreFixedInvestment(**investment, type=InvestmentsType.PRE_FIXED)
        if _type == InvestmentsType.POST_FIXED:
            return PostFixedInvestment(**investment, type=InvestmentsType.POST_FIXED)
        if _type == InvestmentsType.CHECKING_ACCOUNT:
            return CheckingAccountInvestment(**investment, type=InvestmentsType.CHECKING_ACCOUNT)
        raise TypeError
