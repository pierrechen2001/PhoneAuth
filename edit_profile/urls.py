"""
編輯個人資料 URL 路由

定義個人資料編輯相關的 API 路由。
"""

from django.urls import path
from . import views

app_name = 'edit_profile'

urlpatterns = [
    # 獲取個人資料
    path('profile/', views.get_profile, name='get_profile'),
    
    # 更新個人資料
    path('profile/', views.update_profile, name='update_profile'),
    
    # 上傳頭像
    path('avatar/upload/', views.upload_avatar, name='upload_avatar'),
    
    # 刪除頭像
    path('avatar/', views.delete_avatar, name='delete_avatar'),
]

