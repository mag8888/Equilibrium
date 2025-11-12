from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class HealthEndpointTests(APITestCase):
    def test_health_status(self):
        url = reverse('api-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
