import json
import multiprocessing
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from multiprocessing import Pool, Queue


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        func_time = end - start
        print(f"Время выполнения функции {func.__name__}: {func_time:.4f} сек.")
        return {func.__name__: round(func_time, 2)}

    return wrapper


def generate_data(n: int) -> list[int]:
    return [random.randint(1, 1000) for i in range(n)]


def process_number(number: int) -> int:
    factorial = 1

    for i in range(2, number + 1):
        factorial *= i

    return factorial


def save_data_to_file(file_path: str, data: list) -> None:
    with open(file_path, "w", encoding="utf8") as f:
        for item in data:
            f.write(f"{json.dumps(item)}\n")


@timer
def process_simple(numbers: list) -> None:
    for number in numbers:
        process_number(number)


@timer
def process_numbers_with_threads_pool(numbers: list) -> None:
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_number, numbers)


@timer
def process_numbers_with_multiprocessing_pool(numbers: list) -> None:
    with Pool(processes=6) as pool:
        pool.map(process_number, numbers)


def worker(q_in: Queue):
    # с помощью iter
    # for number in iter(q_in.get, None):
    #     process_number(number)

    while True:
        number = q_in.get()
        if number is None:
            break
        else:
            process_number(number)


@timer
def process_numbers_with_multiprocessing_queue(numbers: list):
    number_of_processes = 4
    queue = Queue()

    for number in numbers:
        queue.put(number)

    procs = []
    for _ in range(number_of_processes):
        process = multiprocessing.Process(target=worker, args=(queue,))
        procs.append(process)
        process.start()

    for _ in range(number_of_processes):
        queue.put(None)

    for proc in procs:
        proc.join()


if __name__ == "__main__":
    data = generate_data(100000)
    funcs = [
        process_simple,
        process_numbers_with_threads_pool,
        process_numbers_with_multiprocessing_pool,
        process_numbers_with_multiprocessing_queue,
    ]

    results = [func(data) for func in funcs]

    save_data_to_file(f"{__file__}_results.jsonl", results)
