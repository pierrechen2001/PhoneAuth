"""
個人資料編輯 Serializers

定義請求/回應的數據序列化邏輯。
"""

from rest_framework import serializers
from .models import UserProfile

class UpdateProfileSerializer(serializers.Serializer):
    """
    更新個人資料序列化器
    
    用於驗證和序列化更新個人資料的請求數據。
    """
    
    nickname = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text='使用者暱稱'
    )
    
    gender = serializers.CharField(
        max_length=1,
        required=False,
        allow_blank=True,
        help_text='使用者性別'
    )
    
    age = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True,
        help_text='使用者年齡'
    )
    
    degree = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text='使用者學歷'
    )
    
    motivation_1 = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='動機1'
    )
    
    motivation_2 = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='動機2'
    )
    
    motivation_3 = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='動機3'
    )


class ProfileResponseSerializer(serializers.Serializer):
    """
    個人資料回應序列化器
    
    用於序列化返回給前端的個人資料數據。
    """
    
    id = serializers.UUIDField(
        help_text='Profile ID'
    )
    
    username = serializers.CharField(
        source='user.username',
        help_text='使用者帳號'
    )
    
    email = serializers.EmailField(
        source='user.email',
        help_text='使用者電郵'
    )
    
    nickname = serializers.CharField(
        help_text='使用者暱稱'
    )
    
    gender = serializers.CharField(
        help_text='使用者性別'
    )
    
    age = serializers.CharField(
        help_text='使用者年齡'
    )
    
    degree = serializers.CharField(
        help_text='使用者學歷'
    )
    
    motivation_1 = serializers.CharField(
        allow_null=True,
        help_text='動機1'
    )
    
    motivation_2 = serializers.CharField(
        allow_null=True,
        help_text='動機2'
    )
    
    motivation_3 = serializers.CharField(
        allow_null=True,
        help_text='動機3'
    )
    
    phone_number = serializers.CharField(
        source='user.phone_number',
        allow_null=True,
        allow_blank=True,
        help_text='使用者手機號碼'
    )
    
    phone_verified = serializers.BooleanField(
        source='user.phone_verified',
        help_text='手機是否已驗證'
    )
    
    avatar_url = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        help_text='頭像 URL'
    )


class AvatarUploadSerializer(serializers.Serializer):
    """
    頭像上傳序列化器
    
    用於驗證和序列化上傳頭像的請求數據。
    """
    
    avatar = serializers.ImageField(
        required=True,
        help_text='使用者頭像圖片'
    )


class AvatarResponseSerializer(serializers.Serializer):
    """
    頭像上傳回應序列化器
    
    用於序列化返回給前端的頭像上傳結果。
    """
    
    id = serializers.UUIDField(
        help_text='Profile ID'
    )
    
    avatar_url = serializers.CharField(
        help_text='上傳後的頭像 URL'
    )
    
    avatar_uploaded_at = serializers.DateTimeField(
        help_text='頭像上傳時間'
    )

