import logging
from functools import wraps


def create_logger(level=logging.INFO):
    logging.basicConfig(
        level=level, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def logexceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            create_logger().exception(e)
            raise

    return wrapper
