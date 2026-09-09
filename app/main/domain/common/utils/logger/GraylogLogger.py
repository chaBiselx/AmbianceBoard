"""Logger that sends application events to Graylog through GELF over UDP."""

import json
import socket
import time

from .ILogger import ILogger
from main.domain.common.utils.settings import Settings


class GraylogLogger(ILogger):
    """Send structured log events to a Graylog GELF UDP input."""

    def __init__(self, logger_name: str = 'main'):
        if not logger_name:
            raise ValueError("Le nom du logger ne peut pas être vide")

        self._logger_name = logger_name
        self._graylog_host = Settings.get('GRAYLOG_HOST') or 'graylog'
        self._graylog_port = int(Settings.get('GRAYLOG_PORT') or 12201)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def debug(self, message: str, *args, **kwargs) -> None:
        self._log('debug', message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self._log('info', message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self._log('warning', message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._log('error', message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self._log('critical', message, *args, **kwargs)

    def exception(self, message: str, *args, exc_info: bool = True, **kwargs) -> None:
        self._log('error', message, *args, **kwargs)

    def _log(self, level: str, message: str, *args, **kwargs) -> None:
        if args:
            try:
                message = message % args
            except (TypeError, ValueError):
                pass

        event = {
            'version': '1.1',
            'host': 'ambianceboard',
            'short_message': str(message),
            'timestamp': time.time(),
            'level': self._syslog_level(level),
            '_application': 'ambianceboard',
            '_logger': self._logger_name,
            '_log_level': level,
        }
        extra_fields = kwargs.get('extra_fields') or {}
        event.update({f'_{key}': value for key, value in extra_fields.items()})

        try:
            payload = json.dumps(event, default=str).encode('utf-8')
            self._socket.sendto(payload, (self._graylog_host, self._graylog_port))
        except (OSError, TypeError, ValueError):
            pass

    @staticmethod
    def _syslog_level(level: str) -> int:
        return {'debug': 7, 'info': 6, 'warning': 4, 'error': 3, 'critical': 2}.get(level, 6)

    def flush(self) -> None:
        pass

    def shutdown(self) -> None:
        try:
            self._socket.close()
        except OSError:
            pass

    @property
    def logger_name(self) -> str:
        return self._logger_name

    def __str__(self) -> str:
        return f"GraylogLogger(name='{self._logger_name}', host='{self._graylog_host}')"