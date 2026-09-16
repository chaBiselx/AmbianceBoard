import logging
import threading

from main.domain.common.utils.logger.LoggerFactory import LoggerFactory


class AppLoggerHandler(logging.Handler):
    """Adapt standard-library records to the application logger abstraction."""

    _emit_state = threading.local()

    def __init__(self):
        super().__init__()
        self._logger = LoggerFactory.get_default_logger('application')

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(self._emit_state, 'active', False):
            return

        self._emit_state.active = True
        try:
            message = record.getMessage()
            if record.exc_info:
                message = f'{message}\n{self.formatException(record.exc_info)}'

            extra_fields = {
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'pathname': record.pathname,
                'line': record.lineno,
                'process': record.process,
                'thread': record.thread,
            }

            log_method = getattr(self._logger, record.levelname.lower(), self._logger.info)
            log_method(message, extra_fields=extra_fields)
        except Exception:
            # Logging must never break the application that emitted the record.
            pass
        finally:
            self._emit_state.active = False

    def close(self) -> None:
        try:
            self._logger.shutdown()
        except Exception:
            pass
        super().close()