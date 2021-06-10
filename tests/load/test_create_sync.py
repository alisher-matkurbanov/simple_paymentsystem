import time

import random
import string
import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s: %(message)s',
    level=logging.INFO
)


def rand_string(length=32):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_account():
    resp = requests.post(
        "http://localhost:8000/accounts",
        json={"name": "test name"}
    )
    if resp.status_code != 201:
        logger.info(resp.status_code, resp.json())


def create_accounts(num_accounts: int):
    for i in range(num_accounts):
        create_account()


s = time.time()
create_accounts(5000)
logger.info(f"time elapsed: {time.time() - s}")
