from flask import Flask, request, g

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
        url in the request is exempty from audit logging
        """
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'/foo/bar']
        }
        middleware = AuditLogMiddleware(app)

        with app.test_request_context('/'):
            # Call the _before_request function
            app.preprocess_request()
            self.assertFalse(hasattr(request, 'audit_log'))

    @patch('flask_audit_log.middleware.FlaskAuditLogger')
    def test_before_request_user_callable(self, mocked_audit_log, mock_send_log):
        """
        Test and assert that the audit log will not be attached to the request if the
        url in the request is exempty from audit logging
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
            

    def test_before_request_exempt_urls(self, mock_send_log):
        """
        Test and assert that the audit log will not be attached to the request if the
        url in the request is exempty from audit logging
        """
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'/foo/bar']
        }
        middleware = AuditLogMiddleware(app)
        
        with app.test_request_context('/'):
            # Call the _before_request function
            app.preprocess_request()
            self.assertFalse(hasattr(request, 'audit_log'))

    def test_exempt_url(self, mock_send_log):
        app = Flask('test')
        app.config['AUDIT_LOG'] = {
            'EXEMPT_URLS': [r'^/foo/bar$']
        }
        middleware = AuditLogMiddleware(app)

        self.assertTrue(middleware._exempt_url('/foo/bar'))

        self.assertFalse(middleware._exempt_url('/foo/bar2'))

'''
    @patch('django_audit_log.middleware.DjangoAuditLogger')
    def test_process_response(self, mocked_audit_log):
        """
        Assert that the response has been added to the audit log and
        that the log has been fired.
        """
        # prepare request
        request = self.request_factory.get('/')
        self.middleware.process_request(request)

        # prepare response
        response = View.as_view()(request)
        self.middleware.process_response(request, response)

        mocked_instance = mocked_audit_log.return_value
        mocked_instance.set_django_http_response.assert_called_with(response)
        mocked_instance.send_log.assert_called_with()

    @patch('django_audit_log.middleware.DjangoAuditLogger')
    def test_process_response_without_audit_log(self, mocked_audit_log):
        """
        Assert that when the audit log does not exist, we do not try to call any
        methods on it
        """
        # prepare request (but don't pass through middleware, so that hasattr(request, 'audit_log') is False
        request = self.request_factory.get('/')
        self.assertFalse(hasattr(request, 'audit_log'), "Audit log should not have been attached to request")

        # prepare response
        response = View.as_view()(request)
        self.middleware.process_response(request, response)

        mocked_instance = mocked_audit_log.return_value
        mocked_instance.set_http_response.assert_not_called()
        mocked_instance.send_log.assert_not_called()


'''

def test_get_user_from_request():
    return {
        'authenticated': True,
        'provider': 'test',
        'realm': 'test',
        'email': 'user@test.nl',
        'roles': ['test_role'],
        'ip': '127.0.0.1'
    }
