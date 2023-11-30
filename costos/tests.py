from django.test import TestCase
from rest_framework.test import RequestsClient

# Create your tests here.
client = RequestsClient()
response = client.get('http://testserver/costos/products/')
assert response.status_code == 200

