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

if [ "$RUNCRON" != "1" ]; then

    # python manage.py flush --no-input
    python manage.py migrate

fi

# Démarrer Celery en arrière-plan
celery -A main worker --queues=default --concurrency=4 --loglevel=info &

if [ "$RUNCRON" = "1" ]; then
    echo "Adding crontab..."
    python manage.py crontab add

    sleep 60

    echo "Starting cron..."
    exec cron -f &
fi

if [ "$RUNCRON" != "1" ]; then
    echo "Start WebSocket Daphne..."
    exec daphne parameters.asgi:application --bind 0.0.0.0 --port ${WS_PORT:-8000} &
fi



exec "$@"
