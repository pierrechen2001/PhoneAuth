# 部署指南

本文件說明如何將手機驗證 API 部署到生產環境。

## 📋 部署前檢查清單

- [ ] 已設定生產環境的資料庫（PostgreSQL/MySQL）
- [ ] 已準備好 Firebase Service Account 憑證
- [ ] 已設定環境變數
- [ ] 已準備好 HTTPS 憑證
- [ ] 已設定 CORS 允許的域名
- [ ] 已設定正確的 ALLOWED_HOSTS

## 🔧 環境變數設定

### 必要環境變數

```bash
# Django 核心設定
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 資料庫設定
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Firebase 設定
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-service-account.json

# CORS 設定
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## 🗄️ 資料庫設定

### PostgreSQL（建議）

1. 安裝 PostgreSQL 驅動：
```bash
pip install psycopg2-binary
```

2. 修改 `settings.py`：
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://user:password@localhost:5432/dbname',
        conn_max_age=600
    )
}
```

3. 執行遷移：
```bash
python manage.py migrate
```

### MySQL

1. 安裝 MySQL 驅動：
```bash
pip install mysqlclient
```

2. 修改 `settings.py`：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 🚀 部署方式

### 方式 1：使用 Gunicorn + Nginx（推薦）

#### 1. 安裝 Gunicorn

```bash
pip install gunicorn
```

#### 2. 建立 Gunicorn 設定檔

建立 `gunicorn_config.py`：

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
keepalive = 5
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

#### 3. 啟動 Gunicorn

```bash
gunicorn config.wsgi:application -c gunicorn_config.py
```

#### 4. 設定 Nginx

建立 Nginx 設定檔 `/etc/nginx/sites-available/phone_auth`：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 憑證
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    # SSL 設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Proxy 設定
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    # 日誌
    access_log /var/log/nginx/phone_auth_access.log;
    error_log /var/log/nginx/phone_auth_error.log;
}
```

#### 5. 啟用 Nginx 設定

```bash
sudo ln -s /etc/nginx/sites-available/phone_auth /etc/nginx/sites-enabled/
sudo nginx -t  # 測試設定
sudo systemctl reload nginx
```

#### 6. 設定 Systemd Service

建立 `/etc/systemd/system/phone_auth.service`：

```ini
[Unit]
Description=Phone Authentication API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn config.wsgi:application -c gunicorn_config.py

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl daemon-reload
sudo systemctl start phone_auth
sudo systemctl enable phone_auth
sudo systemctl status phone_auth
```

### 方式 2：使用 Docker

#### 1. 建立 Dockerfile

```dockerfile
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 收集靜態檔案
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 啟動指令
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### 2. 建立 docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: phone_auth
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - ./firebase-service-account.json:/app/firebase-service-account.json
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=postgresql://postgres:your_password@db:5432/phone_auth
      - FIREBASE_CREDENTIALS_PATH=/app/firebase-service-account.json
    depends_on:
      - db

volumes:
  postgres_data:
```

#### 3. 建立並啟動容器

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 方式 3：部署到 Heroku

#### 1. 建立 Procfile

```
web: gunicorn config.wsgi
release: python manage.py migrate
```

#### 2. 建立 runtime.txt

```
python-3.11.0
```

#### 3. 修改 settings.py

```python
# 在 settings.py 最底部加入
import django_heroku
django_heroku.settings(locals())
```

#### 4. 部署

```bash
# 安裝 Heroku CLI
brew install heroku/brew/heroku  # macOS

# 登入
heroku login

# 建立應用
heroku create your-app-name

# 設定環境變數
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# 上傳 Firebase 憑證
heroku config:set FIREBASE_CREDENTIALS="$(cat firebase-service-account.json)"

# 部署
git push heroku main

# 執行遷移
heroku run python manage.py migrate

# 建立超級使用者
heroku run python manage.py createsuperuser
```

## 🔐 安全性設定

### 1. HTTPS 強制

在 `settings.py` 中加入：

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 2. CORS 設定

```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True
```

### 3. 資料庫連線加密

PostgreSQL SSL 設定：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

## 📊 監控與日誌

### 1. 整合 Sentry（錯誤追蹤）

```bash
pip install sentry-sdk
```

在 `settings.py` 中：

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

### 2. 日誌管理

使用 CloudWatch、Papertrail 或 Loggly 等服務收集日誌。

## 🔄 自動部署

### GitHub Actions 範例

建立 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
    
    - name: Deploy to server
      run: |
        # 使用 SSH 部署到你的伺服器
        # 或部署到 Heroku/AWS/GCP
```

## ⚡️ 效能優化

### 1. 使用 Redis 快取

```bash
pip install django-redis
```

在 `settings.py` 中：

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 2. 資料庫連線池

```bash
pip install psycopg2-pool
```

### 3. Static Files CDN

使用 CloudFront、Cloudflare 等 CDN 服務。

## 📝 部署後檢查

- [ ] 可以正常存取 API 端點
- [ ] HTTPS 正常運作
- [ ] 可以正常發送與驗證 OTP
- [ ] Django Admin 可以正常登入
- [ ] API 文件可以正常存取
- [ ] 日誌正常記錄
- [ ] 錯誤監控正常運作
- [ ] 資料庫備份已設定

## 🆘 故障排查

### 常見問題

1. **Static files 無法載入**
   ```bash
   python manage.py collectstatic
   ```

2. **資料庫連線失敗**
   - 檢查防火牆設定
   - 檢查資料庫使用者權限
   - 檢查 DATABASE_URL 環境變數

3. **502 Bad Gateway**
   - 檢查 Gunicorn 是否正在運行
   - 檢查 Nginx 設定
   - 查看錯誤日誌

4. **Firebase 初始化失敗**
   - 確認憑證檔案路徑正確
   - 確認檔案權限正確
   - 檢查環境變數

---

**部署愉快！🚀**

