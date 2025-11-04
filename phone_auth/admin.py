"""
Django Admin 管理介面設定

提供後台管理使用者與 OTP 驗證記錄的功能。
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPVerificationLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """自定義使用者管理介面"""
    
    # 列表頁顯示的欄位
    list_display = [
        'username',
        'email',
        'phone_number',
        'phone_verified',
        'verification_status',
        'otp_attempts',
        'is_active',
        'date_joined',
    ]
    
    # 可搜尋的欄位
    search_fields = ['username', 'email', 'phone_number']
    
    # 篩選器
    list_filter = [
        'phone_verified',
        'verification_status',
        'is_active',
        'is_staff',
        'date_joined',
    ]
    
    # 詳細頁面的欄位分組
    fieldsets = UserAdmin.fieldsets + (
        ('手機驗證資訊', {
            'fields': (
                'phone_number',
                'phone_verified',
                'verification_status',
                'otp_attempts',
                'verification_id',
                'last_otp_sent_at',
            ),
        }),
    )
    
    # 唯讀欄位
    readonly_fields = ['last_otp_sent_at', 'date_joined', 'last_login']
    
    # 每頁顯示數量
    list_per_page = 50


@admin.register(OTPVerificationLog)
class OTPVerificationLogAdmin(admin.ModelAdmin):
    """OTP 驗證記錄管理介面"""
    
    # 列表頁顯示的欄位
    list_display = [
        'id',
        'user',
        'phone_number',
        'action',
        'success',
        'created_at',
    ]
    
    # 可搜尋的欄位
    search_fields = ['user__username', 'phone_number']
    
    # 篩選器
    list_filter = ['action', 'success', 'created_at']
    
    # 詳細頁面的欄位
    fields = [
        'user',
        'phone_number',
        'action',
        'verification_id',
        'success',
        'error_message',
        'created_at',
    ]
    
    # 唯讀欄位（所有欄位都是唯讀，只供查看）
    readonly_fields = fields
    
    # 禁止新增與刪除（記錄只供查看）
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # 每頁顯示數量
    list_per_page = 100
    
    # 預設排序
    ordering = ['-created_at']

