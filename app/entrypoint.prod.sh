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

    echo "Waiting before starting cron..."
    sleep 10

    echo "Starting cron..."
    # Créer les répertoires nécessaires pour cron
    mkdir -p /var/run
    mkdir -p /var/log
    
    # Nettoyer les anciens fichiers PID
    rm -f /var/run/crond.pid

    exec cron -f
fi

if [ "$RUNCRON" != "1" ]; then
    echo "Start WebSocket Daphne..."
    exec daphne parameters.asgi:application --bind 0.0.0.0 --port ${WS_PORT:-8000} &
fi



exec "$@"
