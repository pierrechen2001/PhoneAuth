"""
編輯個人資料 API 測試
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from phone_auth.models import CustomUser


class ProfileUpdateTest(TestCase):
    """個人資料更新測試"""
    
    def setUp(self):
        """設置測試數據"""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_update_profile_success(self):
        """測試成功更新個人資料"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'nickname': 'Test User',
            'gender': 'M',
            'age': '25',
            'degree': 'Bachelor'
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['nickname'], 'Test User')
    
    def test_get_profile_success(self):
        """測試成功獲取個人資料"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/user/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['username'], 'testuser')
    
    def test_update_profile_unauthorized(self):
        """測試未登入狀態下無法更新"""
        data = {
            'nickname': 'Test User'
        }
        
        response = self.client.patch('/api/user/profile/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

