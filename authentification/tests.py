from django.test import TestCase
from django.urls import reverse

from .models import Player

# Create your tests here.

class LoginTestCase(TestCase):
    
    def setUp(self):
        self.user = Player.objects.create_user('TestUser', 'test@test.com', 'test')

    def testLogin(self):
        self.client.login(username='TestUser', password='test')
        response = self.client.get(reverse('auth:login'))
        self.assertEqual(response.status_code, 302)