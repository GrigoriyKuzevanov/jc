import random
import time

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6380,
        max_requests: int = 5,
        interval: int = 3,
    ):
        self._interval = interval
        self._max_requests = max_requests
        self._redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self._key = "requests"

    def test(self) -> bool:
        start_time = time.time()

        self._redis_client.zremrangebyscore(self._key, 0, start_time - self._interval)

        count_requests = self._redis_client.zcard(self._key)

        if count_requests < self._max_requests:
            self._redis_client.zadd(self._key, {start_time: start_time})
            self._redis_client.expire(self._key, self._interval)
            return True

        else:
            return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))
        # time.sleep(0.2)

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
