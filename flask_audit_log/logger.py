import logging

from audit_log.logger import AuditLogger
from flask_audit_log.util import import_callable


class FlaskAuditLogger(AuditLogger):

    def __init__(self, settings={}) -> None:
        self.settings = settings
        super().__init__()

    def get_logger_name(self) -> str:
        logger_name = self.settings.get('LOGGER_NAME')
        if not logger_name:
            return super().get_logger_name()
        return logger_name

    def get_log_handler(self) -> logging.Handler:
        log_handler_path = self.settings.get('LOG_HANDLER_CALLABLE_PATH')
        if not log_handler_path:
            return super().get_log_handler()

        log_handler_callable = import_callable(log_handler_path)
        return log_handler_callable()

    def get_log_formatter(self) -> logging.Formatter:
        log_formatter_path = self.settings.get('LOG_FORMATTER_CALLABLE_PATH')
        if not log_formatter_path:
            return super().get_log_formatter()

        log_formatter_callable = import_callable(log_formatter_path)
        return log_formatter_callable()

    def set_flask_http_request(self, request):
        self.set_http_request(
            method=request.method,
            url=request.url,
            user_agent=request.headers.get('User-Agent', '?')
        )

    def set_flask_http_response(self, response):
        headers = self._get_headers_from_response(response)
        self.set_http_response(
            status_code=getattr(response, 'status_code', ''),
            reason=getattr(response, 'status', ''),
            headers=headers
        )
        return self

    def _get_headers_from_response(self, response) -> dict:
        return {header: value for header, value in response.headers.items()}
