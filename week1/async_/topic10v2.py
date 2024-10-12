import asyncio
import json
import random
import string
import time
from asyncio import Queue
from enum import Enum

import aiofiles
import aiohttp
from aiohttp import ClientSession


class StatusErrorEnum(Enum):
    client_connection_error = 3
    invalid_url = 2
    other_aiohttp_client_error = 1
    other_error = 0
    timeout_error = 408


def generate_urls(number_of_urls: int = 10) -> list[str]:
    return [
        f"http://{''.join(random.choices(string.ascii_letters, k=4))}.com"
        for _ in range(number_of_urls)
    ]


async def fetch_status_code(url: str):
    async with ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                status_code = response.status
        except aiohttp.ClientConnectionError:
            status_code = StatusErrorEnum.client_connection_error.value
        except aiohttp.InvalidURL:
            status_code = StatusErrorEnum.invalid_url.value
        except aiohttp.ClientError:
            status_code = StatusErrorEnum.other_aiohttp_client_error.value
        except asyncio.TimeoutError:
            status_code = StatusErrorEnum.timeout_error.value
        except Exception as error:
            print(f"Ошибка при запросе к {url}: {error}")
            status_code = StatusErrorEnum.other_error.value

        return {"url": url, "status code": status_code}


async def worker(q_urls: Queue, q_results: Queue):
    while True:
        url = await q_urls.get()
        q_urls.task_done()

        if url is None:
            break
        else:
            result = await fetch_status_code(url=url)

            await q_results.put(result)


async def save_to_file(q_results: Queue, file_path: str):
    while True:
        result = await q_results.get()
        q_results.task_done()

        if result is None:
            break
        else:
            async with aiofiles.open(file_path, mode="a", encoding="utf8") as f:
                await f.write(f"{json.dumps(result)}\n")


urls = generate_urls(50)


async def main():
    workers_number = 5
    q_results = Queue(maxsize=5)
    q_urls = Queue(maxsize=5)

    workers = [
        asyncio.create_task(worker(q_urls=q_urls, q_results=q_results))
        for _ in range(workers_number)
    ]

    save_task = asyncio.create_task(
        save_to_file(q_results=q_results, file_path="results.jsonl")
    )

    for url in urls:
        await q_urls.put(url)
    await q_urls.join()

    for _ in range(workers_number):
        await q_urls.put(None)
    await q_urls.join()

    await q_results.put(None)
    await q_results.join()


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Время выполнения: {end - start:.4f} секунд")
