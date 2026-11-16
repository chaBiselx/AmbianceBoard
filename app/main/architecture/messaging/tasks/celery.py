import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parameters.settings")

from kombu import Queue, Exchange
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
from main.domain.common.utils.logger.LoggerFactory import LoggerFactory


def log_worker_started(sender=None, **kwargs):
    worker_name = getattr(sender, "hostname", None) or "unknown"
    LoggerFactory.get_default_logger("celery").info(
        f"Celery worker started: {worker_name}"
    )


def log_worker_stopped(sender=None, **kwargs):
    worker_name = getattr(sender, "hostname", None) or "unknown"
    LoggerFactory.get_default_logger("celery").warning(
        f"Celery worker stopping: {worker_name}"
    )


worker_ready.connect(
    log_worker_started,
    weak=False,
    dispatch_uid="ambianceboard.celery.worker_ready",
)
worker_shutdown.connect(
    log_worker_stopped,
    weak=False,
    dispatch_uid="ambianceboard.celery.worker_shutdown",
)

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['main.domain.brokers.message'])

# Déclaration des queues avec priorité
app.conf.task_queues = [
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-priority': 5}), # Queue par défaut 5: haute priorité / 1: basse priorité
    Queue('music_labeler', Exchange('music_labeler'), routing_key='music_labeler'),  # Queue dédiée, traitée séquentiellement (concurrency=1)
]
