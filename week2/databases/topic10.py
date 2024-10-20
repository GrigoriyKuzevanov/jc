import time
import datetime
from functools import wraps
import redis
import multiprocessing

redis_client = redis.from_url("redis://localhost:6380")


def single(max_processing_time: datetime.timedelta):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}"
            value = "is_processing"
            expire_seconds = int(max_processing_time.total_seconds())
            
            redis_response = redis_client.set(key, value, nx=True, ex=expire_seconds)
            
            if redis_response:
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    redis_client.delete(key)
            else:
                print(f"function {func.__name__} is already running")

        return wrapper
    return decorator


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    print("started processing")
    time.sleep(2)
    print("finished processing")


if __name__ == "__main__":
    p1 = multiprocessing.Process(target=process_transaction, args=[])
    p2 = multiprocessing.Process(target=process_transaction, args=[])
    
    for p in [p1, p2]:
        p.start()
    