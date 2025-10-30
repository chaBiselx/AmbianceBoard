from __future__ import absolute_import, unicode_literals

# Import Celery depuis son nouvel emplacement dans l'architecture messaging
from .architecture.messaging.tasks.celery import app as celery_app

__all__ = ('celery_app',)