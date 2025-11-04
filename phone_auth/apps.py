"""
Phone Auth App 配置
"""

from django.apps import AppConfig


class PhoneAuthConfig(AppConfig):
    """Phone Authentication App 配置類別"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phone_auth'
    verbose_name = '手機驗證'

