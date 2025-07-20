from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Testpass123',
            'phone_number': '9876543210',
            'address': '123 Test St'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        # Registration data
        self.register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Newpass123',
            'confirm_password': 'Newpass123',
            'phone_number': '9876543211',
            'address': '456 New St'
        }
        
        # Login data
        self.login_data = {
            'username_or_phone': 'testuser',
            'password': 'Testpass123'
        }
    
    def test_register_user(self):
        """Test user registration"""
        url = reverse('api:register')
        response = self.client.post(url, self.register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Original + new user
        self.assertEqual(response.data['user']['username'], 'newuser')
    
    def test_login_with_username(self):
        """Test login with username"""
        url = reverse('api:login')
        response = self.client.post(url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])
