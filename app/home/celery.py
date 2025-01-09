from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configure l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parameters.settings")

app = Celery('home')

# Charge les configurations de Celery depuis Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover les tâches dans vos apps Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
