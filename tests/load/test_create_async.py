# modified fetch function with semaphore
import random
import time

import asyncio
from aiohttp import ClientSession

async def fetch(url, session):
    async with session.post(url, json={"name": "alisher"}) as response:
        return await response.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(num):
    url = "http://localhost:8000/accounts"
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for i in range(num):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, url, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

number = 20000
loop = asyncio.get_event_loop()
s = time.time()
future = asyncio.ensure_future(run(number))
loop.run_until_complete(future)
print(f"elapsed time: {time.time() - s}")