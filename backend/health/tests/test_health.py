from unittest.mock import patch

from django.db.utils import OperationalError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTests(APITestCase):
    def test_health_check_success(self):
        """
        Ensure health check returns 200 OK and status 'ok' when DB is connected.
        """
        url = reverse("health_check")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"status": "ok", "database": "connected"}
        )

    @patch("django.db.backends.utils.CursorWrapper")
    def test_health_check_db_failure(self, mock_cursor):
        """
        Ensure health check returns 503 Service Unavailable when DB is disconnected.
        """
        # Mocking the cursor to raise OperationalError when accessed
        mock_cursor.side_effect = OperationalError("DB connection failed")

        # In the view: db_conn.cursor()
        # We can patch 'django.db.backends.base.base.BaseDatabaseWrapper.cursor'
        with patch(
            "django.db.backends.base.base.BaseDatabaseWrapper.cursor",
            side_effect=OperationalError
        ):
             url = reverse("health_check")
             response = self.client.get(url)
             self.assertEqual(
                 response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
             )
             self.assertEqual(
                 response.data, {"status": "error", "database": "disconnected"}
             )
