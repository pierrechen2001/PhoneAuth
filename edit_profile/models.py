"""
編輯個人資料相關的模型
"""

from django.db import models
from django.conf import settings
import uuid


class UserProfile(models.Model):
    ''' User Profile '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    nickname = models.CharField(max_length=150)
    gender = models.CharField(max_length=1)
    age = models.CharField(max_length=10)
    degree = models.CharField(max_length=20)
    counseling_record = models.IntegerField(default=0)
    motivation_1 = models.CharField(max_length=100, null=True, blank=True)
    motivation_2 = models.CharField(max_length=100, null=True, blank=True)
    motivation_3 = models.CharField(max_length=100, null=True, blank=True)
    on_stage = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    retry_time = models.DateTimeField(null=True, blank=True)
    monkey_try = models.IntegerField(default=0)
    
    # 頭像相關欄位
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='個人照片',
        help_text='使用者的個人頭像'
    )
    
    avatar_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='頭像 URL',
        help_text='個人照片的 URL 路徑'
    )
    
    avatar_uploaded_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='頭像上傳時間',
        help_text='最後一次上傳頭像的時間'
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
