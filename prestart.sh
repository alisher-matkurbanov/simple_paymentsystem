# prestart.sh

echo "Waiting for postgres connection"

while ! nc -z db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

# apply migrations
cd ./app
alembic upgrade head

exec "$@"