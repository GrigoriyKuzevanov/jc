import time
import datetime
from functools import wraps


def single(max_processing_time: datetime):
    def decorator(func):
        @wraps
        def wrapper(*args, **kwargs):
            func()

        return wrapper
    return decorator


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    time.sleep(2)


