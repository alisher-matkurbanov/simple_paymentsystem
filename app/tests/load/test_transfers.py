import json
import time

import asyncio
from aiohttp import ClientSession
import argparse


async def post_fetch(url, data, session):
    async with session.post(url, json=data) as response:
        res = await (response.read())
        return response.status, json.loads(res)


async def bound_post_fetch(sem, url, data, session):
    # Getter function with semaphore.
    async with sem:
        return await post_fetch(url, data, session)


async def get_fetch(url, session):
    async with session.get(url) as response:
        return await response.read()


async def bound_get_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        return await get_fetch(url, session)


async def create_accounts(num):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)
    
    # Create client session that will ensure we dont open new connection
    # per each request.
    data = {"name": "testname"}
    url = "http://127.0.0.1:80/accounts"
    async with ClientSession() as session:
        for i in range(num):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_post_fetch(sem, url, data, session))
            tasks.append(task)
        
        responses = asyncio.gather(*tasks)
        await responses
        return responses


async def replenish_wallets(results):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)
    
    # Create client session that will ensure we dont open new connection
    # per each request.
    url = "http://127.0.0.1:80/replenish"
    async with ClientSession() as session:
        for account in results:
            # pass Semaphore and session to every GET request
            data = {
                "wallet_id": account["wallet_id"],
                "amount": "100000000.01",
                "currency": "USD",
            }
            task = asyncio.ensure_future(bound_post_fetch(sem, url, data, session))
            tasks.append(task)
        
        responses = asyncio.gather(*tasks)
        await responses
        return responses


async def transfer_money(from_accounts, to_accounts):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)
    
    # Create client session that will ensure we dont open new connection
    # per each request.
    url = "http://127.0.0.1:80/transfer"
    async with ClientSession() as session:
        for fa, ta in zip(from_accounts, to_accounts):
            # pass Semaphore and session to every GET request
            data = {
                "from_wallet_id": fa["wallet_id"],
                "from_currency": "USD",
                "to_wallet_id": ta["wallet_id"],
                "to_currency": "USD",
                "amount": "5000.91",
            }
            task = asyncio.ensure_future(bound_post_fetch(sem, url, data, session))
            tasks.append(task)
        
        responses = asyncio.gather(*tasks)
        await responses
        return responses


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="make loading to api")
    parser.add_argument("--accounts", type=int, help="num accounts to create", required=True)
    args = parser.parse_args()
    
    is_testing = input("Did you set TESTING=0 in .env? (y/n) ")
    if is_testing.lower() not in ("yes", "y"):
        print("Please set TESTING=0 in .env to run this test")
        exit(1)
    
    number = args.accounts
    loop = asyncio.get_event_loop()
    # create accounts
    s1 = time.time()
    future = asyncio.ensure_future(create_accounts(number))
    created_accounts = loop.run_until_complete(future)
    print(f"create {number} accounts time: {time.time() - s1} s")
    created_accounts = [d for s, d in created_accounts.result() if s == 201]
    print(f"{len(created_accounts)} accounts created successfully")
    # replenish wallets
    s2 = time.time()
    future = asyncio.ensure_future(replenish_wallets(created_accounts))
    replenished = loop.run_until_complete(future)
    print(f"replenish {number} accounts time: {time.time() - s2} s")
    replenished_wallets = [d for s, d in replenished.result() if s == 200]
    print(f"{len(replenished_wallets)} wallets replenished successfully")
    # transfer money
    s3 = time.time()
    future = asyncio.ensure_future(
        transfer_money(created_accounts[:int(number / 2)], created_accounts[int(number / 2):])
    )
    transferred = loop.run_until_complete(future)
    print(f"{number / 2} transfers made during time: {time.time() - s3} s")
    transfers = [d for s, d in transferred.result() if s == 200]
    print(f"{len(transfers)} transfers made successfully")
    # count stats
    print(f"overall time: {time.time() - s1}")
    rps = int((2.5 * number) / int(time.time() - s1)) if int(s2) != 0 else 0
    print(f"average load: {rps} rps")
