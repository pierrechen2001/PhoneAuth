"""
主 URL 路由設定

整合所有 API 端點與 OpenAPI 文件。
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # 手機驗證 API
    path('auth/phone/', include('phone_auth.urls')),
    
    # OpenAPI Schema (JSON/YAML)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI (互動式 API 文件)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc (替代的 API 文件介面)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

