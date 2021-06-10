###simple payment system

https://habr.com/ru/post/480394/

https://www.encode.io/databases/database_queries/
https://fastapi.tiangolo.com/advanced/async-sql-databases/
https://fastapi.tiangolo.com/tutorial/sql-databases/


добавить репозиторий
todo параметризовать алембик в докере
todo приделать идемпотентность
todo разбить на файлы

# CREATE DATABASE yourdbname;
# CREATE USER youruser WITH ENCRYPTED PASSWORD 'yourpass';
# GRANT ALL PRIVILEGES ON DATABASE yourdbname TO youruser;




# accounts
# - account_id: UUID
# - name: String
# - active: Bool
# - created_at
# - updated_at

# wallet 1 - 1 to accounts
# - account_id: UUID
# - wallet_id: UUID
# - currency_id: int
# - amount: Decimal
# - active: Bool
# - created_at
# - updated_at

# currency
# - code

# journal
# - journal_id
# - transaction_type
# - created_at

# posting
# - posting_id
# - journal_id
# - wallet_id
# - amount
# - currency_id

Без докера ~1150 RPS на create account

# Тесты
https://testdriven.io/blog/fastapi-crud/