"""
Gunicorn configuration for AmbianceBoard production deployment.

This file documents best practices and can be used via:
    gunicorn parameters.wsgi:application -c gunicorn_config.py
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('WEB_PORT', 8000)}"

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', 3))
worker_class = "sync"  # Synchronous workers for Django

# Worker lifecycle
worker_connections = 1000
keepalive = 5

# Request handling
max_requests = 1000  # Recycle worker after N requests (prevents memory leaks)
max_requests_jitter = 100  # Add randomness to prevent thundering herd

# Worker timeout - CRITICAL for proper shutdown
# Set to 120 seconds to allow logger shutdown operations (flush + thread join + network delays)
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))

# Graceful shutdown
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 30))

# Logging
accesslog = "/usr/src/app/logs/gunicorn_access.log"
errorlog = "/usr/src/app/logs/gunicorn_error.log"
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'ambianceboard'

# Debugging (useful for development)
# debug = True
