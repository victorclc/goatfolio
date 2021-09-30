def get_event_subject(event: dict):
    try:
        return event["requestContext"]["authorizer"]["claims"]["sub"]
    except KeyError:
        return None


def get_path_param(event: dict, param_name: str):
    try:
        return event["pathParameters"][param_name]
    except KeyError:
        return None


def get_query_param(event: dict, param_name: str):
    try:
        return event["queryStringParameters"][param_name]
    except KeyError:
        return ""


def get_query_params(event: dict):
    try:
        return event["queryStringParameters"]
    except KeyError:
        return None
