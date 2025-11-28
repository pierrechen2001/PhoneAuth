"""
編輯個人資料 API 測試
"""

import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from phone_auth.models import CustomUser
from .models import UserProfile


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
        # 不預先建立 UserProfile，測試自動建立功能
    
    def test_update_profile_success(self):
        """測試成功更新個人資料（自動建立 Profile）"""
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
        
        # 驗證 DB 中已建立 Profile
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.nickname, 'Test User')
    
    def test_get_profile_success(self):
        """測試成功獲取個人資料"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/user/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['username'], 'testuser')
        
        # 驗證 DB 中已建立 Profile
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
    
    def test_update_profile_unauthorized(self):
        """測試未登入狀態下無法更新"""
        data = {
            'nickname': 'Test User'
        }
        
        response = self.client.patch('/api/user/profile/', data, format='json')
        
        # DRF 在未認證時返回 403 Forbidden 而不是 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AvatarUploadTest(TestCase):
    """頭像上傳測試"""
    
    def setUp(self):
        """設置測試數據"""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='avatartest',
            email='avatar@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 創建一個最小的有效 PNG 圖片數據
        self.image_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
    
    def test_upload_avatar_success(self):
        """測試成功上傳頭像"""
        avatar_file = SimpleUploadedFile(
            name='av_test.png',
            content=self.image_data,
            content_type='image/png'
        )
        
        response = self.client.post(
            '/api/user/avatar/upload/',
            {'avatar': avatar_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('avatar_url', response.data['data'])
        self.assertIsNotNone(response.data['data']['avatar_url'])
        
        # 驗證資料庫中的頭像已更新
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile.avatar)
        self.assertIsNotNone(profile.avatar_uploaded_at)
    
    def test_upload_avatar_unauthorized(self):
        """測試未登入狀態下無法上傳頭像"""
        client = APIClient()  # 未認證的客戶端
        
        avatar_file = SimpleUploadedFile(
            name='av_test.png',
            content=self.image_data,
            content_type='image/png'
        )
        
        response = client.post(
            '/api/user/avatar/upload/',
            {'avatar': avatar_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_upload_avatar_file_too_large(self):
        """測試上傳過大的檔案（超過 5MB）"""
        # 創建一個超過 5MB 的假檔案
        large_file = SimpleUploadedFile(
            name='large_image.png',
            content=b'x' * (6 * 1024 * 1024),  # 6MB
            content_type='image/png'
        )
        
        response = self.client.post(
            '/api/user/avatar/upload/',
            {'avatar': large_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'FILE_TOO_LARGE')
    
    def test_upload_avatar_invalid_format(self):
        """測試上傳無效的檔案格式"""
        # 創建一個非圖片檔案
        text_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is not an image',
            content_type='text/plain'
        )
        
        response = self.client.post(
            '/api/user/avatar/upload/',
            {'avatar': text_file},
            format='multipart'
        )
        
        # 應該返回驗證錯誤
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_delete_avatar_success(self):
        """測試成功刪除頭像"""
        # 先上傳一個頭像
        avatar_file = SimpleUploadedFile(
            name='av_test.png',
            content=self.image_data,
            content_type='image/png'
        )
        
        # 上傳頭像
        self.client.post(
            '/api/user/avatar/upload/',
            {'avatar': avatar_file},
            format='multipart'
        )
        
        # 驗證頭像已上傳
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile.avatar)
        
        # 刪除頭像
        response = self.client.delete('/api/user/avatar/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 驗證資料庫中的頭像已刪除
        profile.refresh_from_db()
        self.assertFalse(profile.avatar)  # ImageField 在刪除後為 False
        self.assertIsNone(profile.avatar_uploaded_at)
    
    def test_delete_avatar_when_no_avatar(self):
        """測試刪除不存在的頭像"""
        # 確保沒有頭像
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        if profile.avatar:
            profile.avatar.delete()
            profile.avatar_uploaded_at = None
            profile.save()
        
        # 嘗試刪除頭像
        response = self.client.delete('/api/user/avatar/')
        
        # 應該仍然成功（冪等操作）
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_delete_avatar_unauthorized(self):
        """測試未登入狀態下無法刪除頭像"""
        client = APIClient()  # 未認證的客戶端
        
        response = client.delete('/api/user/avatar/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProfileValidationTest(TestCase):
    """個人資料驗證測試"""
    
    def setUp(self):
        """設置測試數據"""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='validationtest',
            email='validation@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_update_profile_invalid_nickname_length(self):
        """測試暱稱超過最大長度（150字元）"""
        data = {
            'nickname': 'A' * 151  # 超過 150 字元
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'VALIDATION_ERROR')
    
    def test_update_profile_invalid_gender_length(self):
        """測試性別超過最大長度（1字元）"""
        data = {
            'gender': 'MF'  # 超過 1 字元
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_update_profile_invalid_age_length(self):
        """測試年齡超過最大長度（10字元）"""
        data = {
            'age': 'A' * 11  # 超過 10 字元
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_update_profile_invalid_degree_length(self):
        """測試學歷超過最大長度（20字元）"""
        data = {
            'degree': 'A' * 21  # 超過 20 字元
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_update_profile_invalid_motivation_length(self):
        """測試動機超過最大長度（100字元）"""
        data = {
            'motivation_1': 'A' * 101  # 超過 100 字元
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class ProfileBoundaryTest(TestCase):
    """個人資料邊界條件測試"""
    
    def setUp(self):
        """設置測試數據"""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='boundarytest',
            email='boundary@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_update_profile_empty_data(self):
        """測試發送空資料更新"""
        data = {}
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        # 空資料應該被接受（所有欄位都是可選的）
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 驗證 Profile 已建立但欄位未更新
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
    
    def test_update_profile_with_null_values(self):
        """測試使用 null 值更新"""
        # 先建立一個有資料的 Profile
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.nickname = 'Original Nickname'
        profile.save()
        
        # 嘗試用 null 更新
        data = {
            'nickname': None
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        # null 值應該被接受（序列化器允許 null）
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_profile_with_empty_strings(self):
        """測試使用空字串更新"""
        data = {
            'nickname': '',
            'gender': '',
            'age': '',
            'degree': ''
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        # 空字串應該被接受
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_update_profile_max_length_values(self):
        """測試使用最大長度的值更新"""
        data = {
            'nickname': 'A' * 150,  # 正好 150 字元
            'gender': 'M',  # 正好 1 字元
            'age': 'A' * 10,  # 正好 10 字元
            'degree': 'A' * 20,  # 正好 20 字元
            'motivation_1': 'A' * 100  # 正好 100 字元
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        # 最大長度的值應該被接受
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 驗證資料已正確儲存
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(len(profile.nickname), 150)
        self.assertEqual(len(profile.age), 10)
        self.assertEqual(len(profile.degree), 20)
        self.assertEqual(len(profile.motivation_1), 100)
    
    def test_update_profile_partial_update(self):
        """測試部分更新（只更新部分欄位）"""
        # 先建立一個有完整資料的 Profile
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.nickname = 'Original Nickname'
        profile.gender = 'F'
        profile.age = '30'
        profile.save()
        
        # 只更新 nickname
        data = {
            'nickname': 'Updated Nickname'
        }
        
        response = self.client.patch(
            '/api/user/profile/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 驗證只有 nickname 被更新，其他欄位保持不變
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, 'Updated Nickname')
        self.assertEqual(profile.gender, 'F')  # 未改變
        self.assertEqual(profile.age, '30')  # 未改變
    
    def test_get_profile_before_creation(self):
        """測試在 Profile 建立前獲取個人資料"""
        # 確保沒有 Profile
        UserProfile.objects.filter(user=self.user).delete()
        
        response = self.client.get('/api/user/profile/')
        
        # 應該自動建立 Profile 並返回
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 驗證 Profile 已自動建立
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
