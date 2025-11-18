"""
編輯個人資料應用程式配置
"""

from django.apps import AppConfig


class EditProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edit_profile'
    verbose_name = '個人資料編輯'

