from flask import Flask, request, Response

from unittest import TestCase
from unittest.mock import patch

from flask_audit_log.logger import FlaskAuditLogger


class TestLogger(TestCase):

    def setUp(self):
        # creates a test app
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_get_logger_name(self):
        settings = {
            'LOGGER_NAME': 'test_logger_name'
        }
        self.assertEqual(FlaskAuditLogger(settings).get_logger_name(), 'test_logger_name')

    def test_get_logger_name_default(self):
        self.assertEqual(FlaskAuditLogger().get_logger_name(), 'audit_log')

    def test_get_log_handler(self):
        settings = {
            'LOG_HANDLER_CALLABLE_PATH': 'tests.test_logger.get_log_handler'
        }
        self.assertEqual(FlaskAuditLogger(settings).get_log_handler(), get_log_handler())

    @patch('flask_audit_log.logger.AuditLogger.get_log_handler')
    def test_get_log_handler_default(self, mocked_get_log_handler):
        FlaskAuditLogger().get_log_handler()
        mocked_get_log_handler.assert_called_with()

    def test_get_log_formatter(self):
        settings = {
            'LOG_FORMATTER_CALLABLE_PATH': 'tests.test_logger.get_log_formatter'
        }
        self.assertEqual(FlaskAuditLogger(settings).get_log_formatter(), get_log_formatter())

    @patch('flask_audit_log.logger.AuditLogger.get_log_formatter')
    def test_get_log_formatter_default(self, mocked_get_log_formatter):
        FlaskAuditLogger().get_log_formatter()
        mocked_get_log_formatter.assert_called_with()

    def test_set_flask_http_request(self):
        audit_log = FlaskAuditLogger()
        with self.client as c:
            c.get("/foo/bar?querystr=value", headers={'User-Agent': 'test_agent'})
            audit_log.set_flask_http_request(request)

            self.assertEqual(audit_log.http_request['method'], 'GET')
            self.assertEqual(audit_log.http_request['url'], 'http://localhost/foo/bar?querystr=value')
            self.assertEqual(audit_log.http_request['user_agent'], 'test_agent')

    def test_set_flask_http_response(self):
        audit_log = FlaskAuditLogger()
        response = self.client.get("/foo/bar?querystr=value", headers={'User-Agent': 'test_agent'})
        audit_log.set_flask_http_response(response)

        self.assertEqual(audit_log.http_response['status_code'], 404)
        self.assertEqual(audit_log.http_response['reason'], '404 NOT FOUND')
        self.assertTrue('Content-Type' in audit_log.http_response['headers'])

    def test_get_headers_from_response(self):
        expected_headers = {
            'Header1': 'value1',
            'Header2': 'value2',
            'Header3': 'value3'
        }
        response = Response(headers=expected_headers)

        headers = FlaskAuditLogger()._get_headers_from_response(response)

        # Assert that the header we put in, will come out.
        # Note that the HttpResponse class will add a default header
        # 'content-type'.
        for header, expected_value in expected_headers.items():
            self.assertEqual(headers[header], expected_value)


def get_log_handler():
    return 'test_handler'


def get_log_formatter():
    return 'test_formatter'
