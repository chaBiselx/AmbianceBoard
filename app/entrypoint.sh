#!/bin/sh

env >> /etc/environment # give environment variables to cron

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py flush --no-input
python manage.py migrate


# Démarrer Celery en arrière-plan
celery -A home worker --queues=default --concurrency=4 --loglevel=info &

if [ "$RUNCRON" = "1" ]; then
    echo "Adding crontab..."
    python manage.py crontab add

    echo "Starting cron..."
    cron start
fi

exec "$@"
