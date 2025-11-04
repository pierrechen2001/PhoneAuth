"""
URL Routing

定義所有手機驗證相關的 API 路由。
"""

from django.urls import path
from . import views

app_name = 'phone_auth'

urlpatterns = [
    # 發送 OTP 驗證碼
    path('send-otp/', views.send_otp, name='send_otp'),
    
    # 驗證 OTP 代碼
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    # 重新發送 OTP
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]

