### Simple Payment System

**Simple payment system REST API.**  

Allows user:
- create account with wallet
- get account with wallet
- replenish wallet amount
- transfer amount from one wallet to another

Currently supports only USD currency.  
All the operations performs without commision.

#### Built with

- python-3.8
- FastAPI
- PostgreSQL
- [databases](https://github.com/encode/databases) for async work with database
- Alembic for migrations
- Docker with Docker Compose

#### Getting started

Run the project: `docker-compose up --build -d`  
You can change default environment variables in `.env` file.

Run tests:

- set `TESTING=1` in `.env`
- build project:`docker-compose down -v && docker-compose up --build -d`
- run tests: `docker-compsoe exec backend pytest app/tests/unittests -s -vv`

#### Comments

- Used FastAPI as a backend framework because it is simple and performant.
- Used PostgreSQL as a database backend because it's open source, performant and this task required consistency between
  tables (so ACID transactions). Also, PostgreSQL is mature and proven tool for such billing tasks. However,one of the
  disadvantages of using Postgres is that in some performance measures it is slower than mysql. But I used Postgres before so I
  chose this one.  
  To store incoming data I created several tables:
    - `account(id, name, created_at, updated_at)` - store general information about user. Connected with wallet in
      one-to-one relationship.
    - `wallet(id, account_id, amount, currency, created_at, updated_at)` - store information about current account money
    - `currency(code)` - static table with only one currency - `USD`
    - `transaction(id, type, created_at)` - append only table; store information about wallet transactions. Support 2
      types of transaction supported - `replenish` and `transfer`. Row created when replenish wallet or transfer money
      performs.
    - `posting(id, transaction_id, amount, currency)` - append only table; information about transaction amount and
      wallets. It is possible to restore wallet amount depending on `transaction` and this tables. Used to log wallet
      operations.

#### Improvements
There are several improvements in architecture of this system:

- Add some rate limiter to prevent users overuse this API.
- Add Redis or memcached to cache db results of reading operations
  (however I think this system will mostly be used for write operations, so it is not really necessary).
- Add idempotency tokens support to create account, replenish wallet and transfer money methods to handle correctly
  identical sequential operations from one user.
  
