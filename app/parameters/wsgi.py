"""
WSGI config for parameters project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import signal
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parameters.settings")

application = get_wsgi_application()

# Graceful shutdown signal handling to flush logs before worker timeout
def _shutdown_handler(signum, frame):
    """Signal handler for graceful shutdown (SIGTERM, SIGINT)"""
    try:
        from main.domain.common.utils.logger import logger as default_logger
        if hasattr(default_logger, 'shutdown'):
            default_logger.shutdown()
    except Exception:
        pass
    raise SystemExit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, _shutdown_handler)
signal.signal(signal.SIGINT, _shutdown_handler)
