import unittest.mock
from functools import wraps


def lru_cache(func=None, *, maxsize=None):
    wrap_decorator = _lru_cache_wrapper(maxsize=maxsize)

    if func is None:
        return wrap_decorator
    else:
        return wrap_decorator(func)


def _lru_cache_wrapper(maxsize=None):
    def decorator(func):
        cache = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal cache

            args_hash = (
                args
                + tuple(key for key in kwargs)
                + tuple(value for value in kwargs.values())
            )

            for item in cache:
                if args_hash in item:
                    result = item[args_hash]
                    break
            else:
                result = func(*args, **kwargs)
                cache.append({args_hash: result})
                if maxsize and len(cache) > maxsize:
                    del cache[0]

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
