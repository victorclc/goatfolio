import json
from decimal import Decimal


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        # if isinstance(obj, datetime):
        #     return int(obj.timestamp())

        return json.JSONEncoder.default(self, obj)


def dump(_dict):
    return json.dumps(_dict, cls=CustomEncoder)


def load(json_str):
    return json.loads(json_str, parse_float=Decimal)
