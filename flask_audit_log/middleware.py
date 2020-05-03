import re

from flask import g, request

from flask_audit_log.logger import FlaskAuditLogger
from flask_audit_log.util import get_client_ip, import_callable


class AuditLogMiddleware(object):

    def __init__(self, app):
        self.app = app

        # Get the settings from the app config
        self.settings = self.app.config.get('AUDIT_LOG', {})

        exempt_urls = self.settings.get('EXEMPT_URLS', [])
        assert type(exempt_urls) is list, "EXEMPT_URLS must be a list"

        self.redirect_exempt = [re.compile(r) for r in exempt_urls]

        self.setup_audit_log()

    def setup_audit_log(self):
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)
        self.app.teardown_request(self._teardown_request)

    def _before_request(self):
        # Check if the global object doesn't already have an audit_log object or if the path should be skipped
        if hasattr(g, 'audit_log') or self._exempt_url(request.path):
            return

        audit_log = FlaskAuditLogger(self.settings)
        audit_log.set_flask_http_request(request)

        '''
        Get the callable to add the user information to the request.
        Since user managment can be done in many ways in
        Flask, we use a callable to allow users to set the information.
        '''
        user_from_request_callable = self._get_user_from_request_callable()
        if user_from_request_callable:
            user = user_from_request_callable()
        else:
            # if no callable is provided, only get the IP-Adress from the user
            user = {
                'ip': get_client_ip(request)
            }

        audit_log.set_user(
            authenticated=user.get('authenticated', False),
            provider=user.get('provider', ''),
            realm=user.get('realm', ''),
            email=user.get('email', ''),
            roles=user.get('roles', []),
            ip=user.get('ip')
        )

        # Add the audit log to the global request context
        g.audit_log = audit_log

    def _after_request(self, response):
        audit_log = g.audit_log
        audit_log.set_flask_http_response(response)

        return response

    def _teardown_request(self, exception):
        g.audit_log.send_log()

    def _get_user_from_request_callable(self):
        if self.settings.get('USER_FROM_REQUEST_CALLABLE_PATH'):
            user_from_request_callable = import_callable(self.settings.get('USER_FROM_REQUEST_CALLABLE_PATH'))
            return user_from_request_callable
        else:
            return None

    def _exempt_url(self, path):
        return any(pattern.search(path) for pattern in self.redirect_exempt)
