import asyncio
import json
import random
import string
import time
from asyncio import Queue

import aiofiles
from aiohttp import ClientSession


def generate_urls(number_of_urls: int = 10) -> list[str]:
    return [
        f"http://{''.join(random.choices(string.ascii_letters, k=4))}"
        for _ in range(number_of_urls)
    ]


async def fetch_status_code(session: ClientSession, url: str):
    try:
        async with session.get(url) as response:
            status_code = response.status
    except Exception:
        status_code = 0
    return {"url": url, "status code": status_code}


async def worker(q_urls: Queue, q_results: Queue, session):
    while True:
        url = await q_urls.get()
        if url is None:
            await q_results.put(None)
            break
        else:
            result = await fetch_status_code(session=session, url=url)

            await q_results.put(result)
            q_urls.task_done()


async def save_to_file(q_results: Queue, file_path: str):
    async with aiofiles.open(file_path, mode="w", encoding="utf8") as f:
        while True:
            result = await q_results.get()
            if result is None:
                break
            else:
                await f.write(f"{json.dumps(result)}\n")


urls = generate_urls(50)


async def main():
    workers_number = 5
    q_results = Queue(maxsize=5)
    q_urls = Queue(maxsize=5)

    async with ClientSession() as session:
        workers = [
            asyncio.create_task(
                worker(q_urls=q_urls, q_results=q_results, session=session)
            )
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

        await asyncio.gather(*workers, save_task)


start = time.time()
asyncio.run(main())
end = time.time()
print(f"Время выполнения: {end - start:.4f} секунд")
