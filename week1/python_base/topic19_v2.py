import unittest.mock
from functools import wraps
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
import time


def lru_cache(func=None, *, maxsize=None, ttl_seconds=30):
    wrap_decorator = _lru_cache_wrapper(maxsize=maxsize, ttl_seconds=ttl_seconds)

    if func is None:
        return wrap_decorator
    else:
        return wrap_decorator(func)


def _lru_cache_wrapper(maxsize=None, ttl_seconds=30):
    def decorator(func):
        cache = OrderedDict()
        ttl = timedelta(seconds=ttl_seconds)

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal cache

            args_hash = args
            if kwargs:
                for items in kwargs.items():
                    args_hash += items

            if args_hash in cache:
                result, timestamp = cache[args_hash]

                now = datetime.now(timezone.utc)

                if now - timestamp >= ttl:
                    del cache[args_hash]
            else:
                result = func(*args, **kwargs)
                timestamp = datetime.now(timezone.utc)
                cache[args_hash] = result, timestamp

                if maxsize and len(cache.items()) > maxsize:
                    cache.popitem(last=False)

            return result

        return wrapper

    return decorator


@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4

    mocked_func_2 = unittest.mock.Mock()
    mocked_func_2.side_effect = [1, 2]
    decorated = lru_cache(ttl_seconds=2)(mocked_func_2)
    assert decorated(1, 2) == 1
    time.sleep(2)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 2
    assert mocked_func_2.call_count == 2
