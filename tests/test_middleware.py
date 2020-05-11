from flask import Flask, request, g, Response

from unittest import TestCase
from unittest.mock import patch, MagicMock

from flask_audit_log.middleware import AuditLogMiddleware
from flask_audit_log.logger import FlaskAuditLogger

@patch.object(FlaskAuditLogger, 'send_log')
class TestMiddleware(TestCase):

    def setUp(self):
        # creates a test app
        self.app = Flask(__name__)
        self.middleware = AuditLogMiddleware(self.app)
        self.client = self.app.test_client()


    def test_attach_audit_log(self, mock_send_log):
        """
        Assert that the middleware attaches the audit log to the request.
        """
        with self.client as c:
            c.get('/')

            # assert that the audit_log attribute has been added to the global object
            self.assertTrue(hasattr(g, 'audit_log'),
                    "Request should have audit_log attribute after passing through middleware")
            self.assertTrue(isinstance(g.audit_log, FlaskAuditLogger))

    @patch.object(AuditLogMiddleware, '_teardown_request')
    def test_audit_logger_already_attached(self, mock_send_log, mock_teardown_request):
        """
        Assert that the middleware does not attach the audit log again if attribute already exists
        Mock _teardown_request since this is called aftter test_request_context
        """
        app = Flask('test')
        middleware = AuditLogMiddleware(app)

        with app.test_request_context('/'):
            g.audit_log = 'test'

            # Call the _before_request function
            app.preprocess_request()

            self.assertEqual(g.audit_log, 'test', "Expected request.audit_log to not have been modified "
                                                        "because request.audit_log was already present")

    @patch('flask_audit_log.middleware.FlaskAuditLogger')
    def test_before_request_extras(self, mocked_audit_log, mock_send_log):
        """
        Assert that the middleware calls the proper methods to add extras
        to the audit log.
        """
        expected_user = {
            'authenticated': False,
            'provider': '',
            'realm': '',
            'email': '',
            'roles': [],
            'ip': '127.0.0.1'
        }

        with self.client as c:
            c.get('/')

            mocked_instance = mocked_audit_log.return_value
            mocked_instance.set_flask_http_request.assert_called_with(request)
            mocked_instance.set_user.assert_called_with(**expected_user)

    def test_before_request_exempt_urls(self, mock_send_log):
        """
        Test and assert that the audit log will not be attached to the request if the
        url in the request is exempt from audit logging
        """
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'/foo/bar']
        }
        middleware = AuditLogMiddleware(app)

        with app.test_request_context('/'):
            # Call the _before_request function
            app.preprocess_request()
            self.assertTrue(hasattr(g, 'audit_log'))

    @patch('flask_audit_log.middleware.FlaskAuditLogger')
    def test_before_request_user_callable(self, mocked_audit_log, mock_send_log):
        """
        Test to see that the provided callable will be used to collect the user
        information from the request.
        """
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'USER_FROM_REQUEST_CALLABLE_PATH': 'tests.test_middleware.test_get_user_from_request'
        }
        middleware = AuditLogMiddleware(app)

        with app.test_request_context('/'):
            # Call the _before_request function
            app.preprocess_request()

            mocked_instance = mocked_audit_log.return_value
            mocked_instance.set_user.assert_called_with(**test_get_user_from_request())

    @patch('flask_audit_log.middleware.FlaskAuditLogger')
    def test_after_request(self, mocked_audit_log, mock_send_log):
        """
        Test and assert that the response will not be logged to the request if the
        url in the request is exempty from audit logging
        """
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'/foo/bar']
        }
        middleware = AuditLogMiddleware(app)


        with app.test_request_context('/'):
            mocked_instance = mocked_audit_log.return_value

            # Call the _before_request and _after_request function
            app.preprocess_request()

            # Create a mock repsonse
            resp = Response()
            resp = app.process_response(resp)

            mocked_instance.set_flask_http_response.assert_called_with(resp)

    @patch('flask_audit_log.middleware.FlaskAuditLogger')
    def test_after_request_exempt_url(self, mocked_audit_log, mock_send_log):
        """
        Test and assert that the response will not be logged to the request if the
        url in the request is exempty from audit logging
        """
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'/foo/bar']
        }
        middleware = AuditLogMiddleware(app)


        with app.test_request_context('/foo/bar'):
            mocked_instance = mocked_audit_log.return_value

            # Call the _before_request and _after_request function
            app.preprocess_request()

            # Create a mock repsonse
            resp = Response()
            resp = app.process_response(resp)

            mocked_instance.set_flask_http_response.assert_not_called()


    def test_exempt_url(self, mock_send_log):
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'^/foo/bar$']
        }
        middleware = AuditLogMiddleware(app)

        self.assertTrue(middleware._exempt_url('/foo/bar'))

        self.assertFalse(middleware._exempt_url('/foo/bar2'))

def test_get_user_from_request():
    return {
        'authenticated': True,
        'provider': 'test',
        'realm': 'test',
        'email': 'user@test.nl',
        'roles': ['test_role'],
        'ip': '127.0.0.1'
    }
