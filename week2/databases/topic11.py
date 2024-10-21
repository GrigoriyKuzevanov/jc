import json

import redis


class RedisQueue:
    def __init__(self, host: str = "localhost", port: int = 6380):
        self._redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self._key = "queue"

    def publish(self, msg: dict):
        json_msg = json.dumps(msg)
        self._redis_client.rpush(self._key, json_msg)

    def consume(self) -> dict:
        response = self._redis_client.lpop(self._key)
        if response:
            result = json.loads(response)
            return result


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
