# 專案概覽

這份文件提供專案的整體架構與關鍵技術細節說明，適合開發人員快速了解專案。

## 📊 專案統計

- **語言**: Python 3.11+
- **框架**: Django 4.2.7 + Django REST Framework 3.14.0
- **資料庫**: SQLite（可替換為 PostgreSQL/MySQL）
- **認證服務**: Firebase Phone Authentication
- **API 文件**: OpenAPI 3.0 (drf-spectacular)
- **程式碼行數**: 約 2000+ 行
- **模組數量**: 1 個核心模組（phone_auth）

## 🏗 專案架構

```
PhoneOath/
│
├── config/                          # Django 專案設定目錄
│   ├── __init__.py
│   ├── settings.py                 # 主設定檔（重要）
│   ├── urls.py                     # 主路由設定
│   ├── wsgi.py                     # WSGI 入口
│   └── asgi.py                     # ASGI 入口
│
├── phone_auth/                      # 手機驗證核心模組（可獨立複製）
│   ├── __init__.py
│   ├── apps.py                     # App 配置
│   ├── models.py                   # 資料模型（User + OTP Log）
│   ├── serializers.py              # API 序列化器（輸入/輸出格式）
│   ├── views.py                    # API 視圖（業務邏輯）
│   ├── urls.py                     # 模組路由
│   ├── admin.py                    # Django Admin 設定
│   └── firebase_service.py         # Firebase 整合服務
│
├── manage.py                        # Django 管理指令
├── requirements.txt                 # Python 依賴套件
├── .gitignore                       # Git 忽略規則
├── openapi.yaml                     # OpenAPI 規格檔案
│
├── README.md                        # 完整使用說明
├── guides/                          # 操作說明與指南文件
│   ├── QUICK_START.md               # 快速開始指南
│   ├── API_TESTING_GUIDE.md         # API 測試指南
│   ├── DEPLOYMENT_GUIDE.md          # 部署指南
│   ├── PROJECT_OVERVIEW.md          # 本文件
│   └── COMPLETION_SUMMARY.md        # 專案完成總結
├── api_spec.md                     # 原始 API 規格
└── example_test.py                 # Python 測試範例
```

## 🔑 核心模組說明

### 1. models.py - 資料模型

**CustomUser Model**
- 繼承 Django 的 AbstractUser
- 新增欄位：
  - `phone_number`: 完整手機號碼（含國碼）
  - `phone_verified`: 驗證狀態
  - `otp_attempts`: 嘗試次數
  - `verification_status`: 當前狀態
  - `verification_id`: Firebase session ID
  - `last_otp_sent_at`: 最後發送時間（用於 rate limiting）

**OTPVerificationLog Model**（可選）
- 記錄所有 OTP 操作歷史
- 用於追蹤與除錯

**設計考量**:
- 使用 CharField 儲存手機號碼（支援國際格式）
- 使用 DateTimeField + timedelta 實作 rate limiting
- 使用 TextChoices 定義狀態碼（類型安全）

### 2. serializers.py - API 序列化器

**主要 Serializers**:
- `SendOTPSerializer`: 發送 OTP 請求格式
- `VerifyOTPSerializer`: 驗證 OTP 請求格式
- `ResendOTPSerializer`: 重發 OTP 請求格式
- 各自對應的 Response Serializers

**特點**:
- 使用 RegexValidator 驗證格式
- 詳細的 help_text 說明（自動生成 API 文件）
- 驗證方式：verification_id + 6 位 otp_code

### 3. views.py - API 視圖

**API 端點**:
1. `send_otp`: 發送 OTP（POST）
2. `verify_otp`: 驗證 OTP（POST）
3. `resend_otp`: 重新發送 OTP（POST）

**共同特性**:
- 使用 `@api_view` 裝飾器
- 使用 `@permission_classes([IsAuthenticated])` 要求登入
- 完整的錯誤處理
- 記錄日誌到 `OTPVerificationLog`
- 返回結構化的 JSON 回應

**業務邏輯**:
- Rate Limiting: 檢查 `last_otp_sent_at`，限制 60 秒
- 錯誤次數限制: 使用 `otp_attempts` 計數，最多 3 次
- 狀態管理: 使用 `verification_status` 追蹤流程
- 並發處理: 使用資料庫欄位 + transaction（可擴展）

### 4. firebase_service.py - Firebase 整合

**FirebaseAuthService 類別**（單例模式）:
- `send_otp()`: 發送 OTP（實際在前端完成）
- `verify_otp()`: 驗證 6 位 OTP
- `get_user_by_phone()`: 根據手機查詢使用者

**重要說明**:
- Firebase Admin SDK 不直接支援發送 SMS
- 實際 OTP 發送需在前端使用 Firebase JS SDK
- 後端主要負責：
  1. 驗證 6 位 OTP（或與前端確認 verification_id 流程）
  2. 更新使用者資料

### 5. admin.py - Django Admin

提供後台管理介面：
- 使用者管理（包含手機驗證資訊）
- OTP 驗證記錄查看（唯讀）
- 支援搜尋、篩選、排序

## 🔄 完整流程圖

```
前端                         後端（Django）              Firebase
│                           │                          │
├─ 1. 輸入手機號碼          │                          │
│                           │                          │
├─ 2. 呼叫 /send-otp/      ─┼→ 檢查 rate limiting     │
│                           │   更新使用者狀態          │
│                           │   回傳成功               │
│                           │                          │
├─ 3. 使用 Firebase SDK    ─┼─────────────────────────┼→ 發送 SMS
│    signInWithPhoneNumber  │                          │   返回 verificationId
│                           │                          │
├─ 4. 使用者收到 SMS        │                          │
│    輸入驗證碼             │                          │
│                           │                          │
├─ 5. 使用 Firebase SDK    ─┼─────────────────────────┼→ 驗證 OTP
│    confirmationResult     │                          │   返回 user
│    .confirm(code)         │                          │
│                           │                          │
├─ 6. 呼叫 /verify-otp/    ─┼→ 驗證 6 位 OTP ─────────┼→ 後端驗證 OTP
│    傳送 verification_id   │   更新使用者資料          │   返回驗證結果
│    與 otp_code            │                          │
│                           │   phone_verified = True  │
│                           │   回傳成功               │
│                           │                          │
└─ 8. 顯示驗證成功          │                          │
```

## 🔐 安全性設計

### 1. 認證與授權
- 所有 API 端點都需要登入（`IsAuthenticated`）
- 支援多種認證方式：
  - Session Authentication（瀏覽器）
  - Token Authentication（API）
  - Basic Authentication（測試）

### 2. 輸入驗證
- 使用 DRF Serializers 驗證所有輸入
- 使用 RegexValidator 驗證格式
- 防止 SQL Injection（Django ORM）
- 防止 XSS（JSON 回應）

### 3. Rate Limiting
- 使用資料庫欄位實作（`last_otp_sent_at`）
- 60 秒內限制重複請求
- 可擴展使用 Redis 實作分散式 rate limiting

### 4. 錯誤次數限制
- 每個 session 最多錯誤 3 次
- 達到上限自動鎖定
- 重新發送 OTP 後重置

### 5. Firebase Token 驗證
- 以 6 位 OTP 驗證為主（verification_id + otp_code）
- 防止偽造 Token
- 確保手機號碼已由 Firebase 驗證

### 6. HTTPS（生產環境）
- 強制使用 HTTPS
- 設定 HSTS
- Secure Cookie

## 🎯 設計模式

### 1. 單例模式（Singleton）
- `FirebaseAuthService` 使用單例模式
- 確保 Firebase App 只初始化一次

### 2. 依賴注入
- Views 依賴 `firebase_service` 實例
- 方便測試與 mock

### 3. 策略模式
- 本專案採單一路徑：Verification ID + 6 位 OTP 驗證

### 4. Repository 模式（可擴展）
- Models 作為 data layer
- Views 作為 business logic layer
- Serializers 作為 presentation layer

## 📊 資料流

```
Request → DRF Router → View Function → Serializer (驗證) 
   → Business Logic → Firebase Service → Database 
   → Response Serializer → JSON Response
```

## 🧪 測試建議

### 單元測試範圍

1. **Serializers 測試**
   - 驗證格式檢查
   - 邊界值測試
   - 錯誤訊息測試

2. **Views 測試**
   - 正常流程測試
   - 錯誤處理測試
   - Rate limiting 測試
   - 錯誤次數限制測試
   - 權限測試

3. **Models 測試**
   - 欄位驗證
   - 方法測試（reset_otp_attempts, increment_otp_attempts）

4. **Firebase Service 測試**
   - Mock Firebase Admin SDK
   - 測試各種回應情境

### 整合測試

使用 `example_test.py` 進行端到端測試：
```bash
python example_test.py
```

## 🚀 效能考量

### 瓶頸分析

1. **資料庫查詢**
   - 使用 `select_related` 減少查詢次數
   - 為手機號碼欄位建立索引（unique=True 自動建立）

2. **Firebase API 呼叫**
   - Firebase Token 驗證需要網路請求
   - 考慮使用快取（短期有效）

3. **Rate Limiting**
   - 當前使用資料庫實作
   - 高流量時建議使用 Redis

### 擴展性

- **水平擴展**: 無狀態設計，可輕鬆擴展多台伺服器
- **資料庫**: 可替換為 PostgreSQL 支援更高並發
- **快取**: 可整合 Redis 快取 Firebase Token 驗證結果
- **非同步**: 可改為使用 Celery 處理 OTP 發送

## 📝 設定重點

### settings.py 關鍵設定

```python
# User Model
AUTH_USER_MODEL = 'phone_auth.CustomUser'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Firebase
FIREBASE_CREDENTIALS_PATH = '/path/to/firebase-service-account.json'

# Logging
LOGGING = {
    'loggers': {
        'phone_auth': {'level': 'INFO'},
    }
}
```

## 🔄 未來擴展建議

### 功能擴展
1. 支援多個手機號碼綁定
2. 手機號碼變更功能
3. 手機號碼解綁功能
4. 簡訊模板自訂
5. 支援語音驗證

### 技術改進
1. 使用 Redis 實作 rate limiting
2. 使用 Celery 處理非同步任務
3. 新增單元測試與整合測試
4. 實作 API 版本控制
5. 新增 API 使用量統計

### 安全強化
1. 實作 IP 白名單
2. 新增驗證碼複雜度設定
3. 實作裝置指紋識別
4. 新增異常登入偵測
5. 整合 reCAPTCHA

## 📚 相關資源

- [Django 官方文件](https://docs.djangoproject.com/)
- [Django REST Framework 文件](https://www.django-rest-framework.org/)
- [Firebase Admin SDK 文件](https://firebase.google.com/docs/admin/setup)
- [Firebase Phone Auth 文件](https://firebase.google.com/docs/auth/web/phone-auth)
- [OpenAPI 規格](https://swagger.io/specification/)

---

**專案維護**: 定期更新依賴套件，關注安全性更新。

