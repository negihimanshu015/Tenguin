import json
import logging
import unittest

from core.logging import JSONFormatter
from core.middleware import RequestCorrelationMiddleware
from django.test import RequestFactory, SimpleTestCase


class MockResponse(dict):
    def __init__(self):
        self.status_code = 200

class LoggingMiddlewareTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestCorrelationMiddleware(lambda r: MockResponse())

    def test_correlation_id_middleware(self):
        request = self.factory.get('/')
        response = self.middleware(request)

        # Check if X-Correlation-ID is set in response
        self.assertIn('X-Correlation-ID', response)

        # Check if existing correlation ID is preserved
        request_with_id = self.factory.get('/', HTTP_X_CORRELATION_ID='test-id-123')
        response_with_id = self.middleware(request_with_id)
        self.assertEqual(response_with_id['X-Correlation-ID'], 'test-id-123')

class JSONFormatterTest(SimpleTestCase):
    def test_json_formatter(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.correlation_id = 'test-correlation-id'
        record.status_code = 200
        record.duration = 0.123

        formatted = formatter.format(record)
        log_json = json.loads(formatted)

        self.assertEqual(log_json['message'], 'Test message')
        self.assertEqual(log_json['correlation_id'], 'test-correlation-id')
        self.assertEqual(log_json['level'], 'INFO')
        self.assertEqual(log_json['status_code'], 200)
        self.assertEqual(log_json['duration'], 0.123)

if __name__ == '__main__':
    unittest.main()
