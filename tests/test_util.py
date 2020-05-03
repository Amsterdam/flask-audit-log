from flask import Flask, request

from unittest import TestCase
from unittest.mock import patch

from flask_audit_log.util import get_client_ip, import_callable


class TestUtil(TestCase):

    def test_get_client_ip_forwarded(self):
        app = Flask(__name__)

        with app.test_request_context('/', environ_base={'HTTP_X_FORWARDED_FOR': '1.2.3.4'}):
            print(request.headers)
            self.assertEqual(get_client_ip(request), '1.2.3.4')

    def test_get_client_ip(self):
        app = Flask(__name__)

        with app.test_request_context('/', environ_base={'REMOTE_ADDR': '2.3.4.5'}):
            self.assertEqual(get_client_ip(request), '2.3.4.5')

    @patch('logging.Logger.warning')
    def test_get_client_ip_exception(self, mocked_logger):
        self.assertEqual(get_client_ip(request=None), 'failed to get ip')
        mocked_logger.assert_called_with('Failed to get ip for audit log', exc_info=True)

    def test_import_callable(self):
        path = 'tests.test_util.callable_for_test'
        callable = import_callable(path)
        self.assertEqual(callable(), 'success')


def callable_for_test():
    return 'success'
