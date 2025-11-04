"""
Django 設定檔

此檔案包含手機驗證 API 所需的所有設定。
可以將相關設定複製到你現有的 Django 專案中。
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-replace-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',  # Django REST Framework
    'drf_spectacular',  # OpenAPI 文件生成
    'corsheaders',  # CORS 處理
    
    # Local apps
    'phone_auth',  # 手機驗證模組
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS 中介層（需在 CommonMiddleware 之前）
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'phone_auth.CustomUser'


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hant'  # 繁體中文

TIME_ZONE = 'Asia/Taipei'  # 台北時區

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# Django REST Framework 設定
# ============================================================

REST_FRAMEWORK = {
    # 預設權限：需要登入
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # 預設認證方式
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    
    # OpenAPI Schema 設定
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # 分頁設定
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    
    # 錯誤處理
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}


# ============================================================
# OpenAPI / Swagger 文件設定
# ============================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Phone Authentication API',
    'DESCRIPTION': '手機號碼綁定驗證 API\n\n'
                   '提供手機號碼綁定、OTP 發送與驗證功能。\n'
                   '整合 Firebase Phone Authentication。',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # API 端點設定
    'SCHEMA_PATH_PREFIX': '/api/',
    
    # 認證設定
    'COMPONENT_SPLIT_REQUEST': True,
    
    # 語言設定
    'LANGUAGE': 'zh-hant',
}


# ============================================================
# CORS 設定（跨域請求）
# ============================================================

# 開發環境允許所有來源（生產環境應限制特定域名）
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React 開發伺服器
    "http://localhost:8080",  # Vue 開發伺服器
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# 或在開發環境允許所有來源（不建議用於生產環境）
# CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]


# ============================================================
# Firebase 設定
# ============================================================

# Firebase Service Account JSON 檔案路徑
FIREBASE_CREDENTIALS_PATH = config(
    'FIREBASE_CREDENTIALS_PATH',
    default=os.path.join(BASE_DIR, 'firebase-service-account.json')
)


# ============================================================
# Logging 設定
# ============================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'phone_auth.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'phone_auth': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'firebase_admin': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# 確保 logs 目錄存在
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

