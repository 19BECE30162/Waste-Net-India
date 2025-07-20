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
    
    def test_login_with_phone(self):
        """Test login with phone number"""
        url = reverse('api:login')
        login_data = {
            'username_or_phone': '9876543210',
            'password': 'Testpass123'
        }
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])
    
    def test_get_profile_authenticated(self):
        """Test getting user profile when authenticated"""
        # Login first
        login_url = reverse('api:login')
        login_response = self.client.post(login_url, self.login_data, format='json')
        token = login_response.data['tokens']['access']
        
        # Get profile
        url = reverse('api:user_profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_update_profile(self):
        """Test updating user profile"""
        # Login first
        login_url = reverse('api:login')
        login_response = self.client.post(login_url, self.login_data, format='json')
        token = login_response.data['tokens']['access']
        
        # Update profile
        url = reverse('api:user_profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        update_data = {
            'phone_number': '9876543212',
            'address': 'Updated Address'
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '9876543212')
        self.assertEqual(response.data['address'], 'Updated Address')
    
    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        url = reverse('api:register')
        invalid_data = self.register_data.copy()
        invalid_data['confirm_password'] = 'wrongpassword'
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)
