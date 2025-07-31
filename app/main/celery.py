import os
from kombu import Queue, Exchange
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parameters.settings")

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Déclaration des queues avec priorité
app.conf.task_queues = [
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-priority': 5}),
]
