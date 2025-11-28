"""
編輯個人資料 Django Admin 配置
"""

from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'gender', 'age', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'nickname', 'phone_number')
    list_filter = ('gender', 'status', 'on_stage')
    
    def created_at(self, obj):
        return obj.user.date_joined
    created_at.short_description = '建立時間'
