import asyncio
import json
import string
from asyncio import Semaphore
from enum import Enum
import time
import random

import aiohttp


class StatusErrorEnum(Enum):
    client_connection_error = 1
    invalid_url = 2
    other_aiohttp_client_error = 0


URLS = [f"https://{''.join(random.choices(string.ascii_letters, k=7))}" for _ in range(100)]


def write_to_file(data: list, file_path: str):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


async def fetch_status_from_url(
    session: aiohttp.ClientSession, url: str, semaphore: Semaphore
):
    async with semaphore:
        try:
            async with session.get(url) as response:
                status_code = response.status
        except aiohttp.ClientConnectorError:
            status_code = StatusErrorEnum.client_connection_error.value
        except aiohttp.InvalidURL:
            status_code = StatusErrorEnum.invalid_url.value
        except aiohttp.ClientError:
            status_code = StatusErrorEnum.other_aiohttp_client_error.value

        return {"url": url, "status_code": status_code}


async def fetch_urls(urls: list[str], concurrent_requests_constraint: int):
    semaphore = Semaphore(concurrent_requests_constraint)
    async with aiohttp.ClientSession() as session:
        status_tasks = [
            asyncio.create_task(
                fetch_status_from_url(url=url, session=session, semaphore=semaphore)
            )
            for url in urls
        ]

        # status_tasks = []
        #
        # for url in urls:
        #     task = asyncio_.create_task(fetch_status_from_url(url=url, session=session, semaphore=semaphore))
        #     status_tasks.append(task)

        results = await asyncio.gather(*status_tasks, return_exceptions=True)
        print(results)
        return results


if __name__ == "__main__":
    start = time.time()
    result_list = asyncio.run(fetch_urls(URLS, 5))
    write_to_file(result_list, "results.json")
    end = time.time()
    print(f"{end - start:.3f}")
