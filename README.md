# 手機號碼驗證 API 系統

完整的 Django 手機號碼綁定驗證 API，整合 Firebase Phone Authentication。

## 📋 目錄

- [功能特色](#功能特色)
- [技術堆疊](#技術堆疊)
- [系統架構](#系統架構)
- [快速開始](#快速開始)
- [API 端點說明](#api-端點說明)
- [整合到現有專案](#整合到現有專案)
- [前端整合指南](#前端整合指南)
- [常見問題](#常見問題)

---

## 🚀 功能特色

- ✅ 完整的手機號碼綁定與驗證流程
- ✅ 整合 Firebase Phone Authentication
- ✅ OTP 錯誤次數限制（最多 3 次）
- ✅ Rate Limiting（60 秒內限制重複發送）
- ✅ 詳細的 API 文件（OpenAPI/Swagger）
- ✅ 完整的錯誤處理與日誌記錄
- ✅ 支援國際手機號碼（含國碼）
- ✅ 模組化設計，易於整合到現有專案

---

## 🛠 技術堆疊

- **後端框架**: Django 4.2.7
- **API 框架**: Django REST Framework 3.14.0
- **認證服務**: Firebase Admin SDK 6.3.0
- **資料庫**: SQLite（可替換為 PostgreSQL/MySQL）
- **API 文件**: drf-spectacular 0.27.0
- **環境管理**: python-decouple 3.8

---

## 📐 系統架構

```
PhoneOath/
├── config/                     # Django 專案設定
│   ├── __init__.py
│   ├── settings.py             # 主設定檔
│   ├── urls.py                 # 主路由設定、整合 API 與文件
│   ├── wsgi.py
│   └── asgi.py
│
├── phone_auth/                 # 手機驗證模組（可獨立複製）
│   ├── __init__.py
│   ├── models.py               # 資料模型（CustomUser Model + OTPVerificationLog）
│   ├── serializers.py          # API 序列化器（輸入/輸出格式定義）
│   ├── views.py                # API 視圖（3 個 API 端點完整實作）
│   ├── urls.py                 # 路由模組設定
│   ├── firebase_service.py     # Firebase Auth 整合服務
│   ├── admin.py                # Django Admin 設定
│   └── apps.py                 # App 配置
│
├── manage.py                   # Django 管理指令
├── requirements.txt            # Python 套件依賴
├── example_test.py             # Python 測試腳本
├── api_spec.md                 # API 規格說明
├── API_TESTING_GUIDE.md        # API 測試說明指南
├── DEPLOYMENT_GUIDE.md         # 部署說明指南
└── README.md                   # 本文件（完整使用說明）
```

---

## ⚡️ 快速開始

### 1. 環境準備

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. Firebase 設定

#### 2.1 在 Firebase Console 啟用 Phone Authentication

1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 選擇你的專案（或建立新專案）
3. 前往 **Authentication** → **Sign-in method**
4. 啟用 **Phone** 認證方式

#### 2.2 下載 Service Account 金鑰

1. 前往 **Project Settings** → **Service accounts**
2. 點擊 **Generate new private key**
3. 下載 JSON 檔案，重新命名為 `firebase-service-account.json`
4. 將檔案放置於專案根目錄

### 3. 環境變數設定

建立 `.env` 檔案於專案根目錄：

```env
# Django 設定
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Firebase 設定
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-service-account.json
```

### 4. 資料庫初始化

```bash
# 建立資料庫遷移檔案
python manage.py makemigrations

# 執行資料庫遷移
python manage.py migrate

# 建立超級使用者（用於登入 Admin）
python manage.py createsuperuser
```

### 5. 啟動開發伺服器

```bash
python manage.py runserver
```

伺服器將在 `http://127.0.0.1:8000/` 啟動。

### 6. 查看 API 文件

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

---

## 📡 API 端點說明

### Base URL
```
http://127.0.0.1:8000/auth/phone/
```

### 認證要求
所有 API 端點都需要使用者登入。請在 Request Header 中包含認證資訊：

```http
Authorization: Token your-auth-token
```

或使用 Session Authentication（瀏覽器 Cookie）。

---

### 1. 發送 OTP 驗證碼

**Endpoint**: `POST /auth/phone/send-otp/`

**說明**: 發送手機驗證碼到指定號碼。

**Request Body**:
```json
{
  "country_code": "+886",
  "phone_number": "987654321"
}
```

**參數說明**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| country_code | string | ✅ | 國碼（例如：+886 代表台灣） |
| phone_number | string | ✅ | 手機號碼（不含國碼） |

**Response (成功)**:
```json
{
  "status": "OTP_SENT",
  "message": "驗證碼已發送到您的手機，請在前端完成 Firebase Phone Auth 流程",
  "expires_in": 300,
  "note": "前端需使用 Firebase JS SDK 的 signInWithPhoneNumber 方法，並將返回的 verificationId 傳給 verify-otp API"
}
```

**Response (頻率限制)**:
```json
{
  "status": "TOO_MANY_REQUESTS",
  "message": "請求過於頻繁，請等待 45 秒後再試",
  "retry_after": 45
}
```

**錯誤碼**:
- `400 BAD_REQUEST`: 輸入資料格式錯誤
- `429 TOO_MANY_REQUESTS`: 請求過於頻繁（60 秒內重複請求）

---

### 2. 驗證 OTP 代碼

**Endpoint**: `POST /auth/phone/verify-otp/`

**說明**: 驗證使用者輸入的 OTP 代碼。

#### 使用 verification_id + otp_code（唯一方式）

**Request Body**:
```json
{
  "verification_id": "xxxxxx",
  "otp_code": "123456"
}
```


**參數說明**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| verification_id | string | ✅ | Firebase 返回的驗證 session ID |
| otp_code | string | ✅ | 使用者輸入的驗證碼（6 位數字） |

**Response (驗證成功)**:
```json
{
  "status": "VERIFIED",
  "phone_number": "+886987654321",
  "message": "手機號碼驗證成功"
}
```

**Response (驗證失敗)**:
```json
{
  "status": "INVALID_OTP",
  "remaining_attempts": 2,
  "message": "驗證碼錯誤，您還有 2 次機會"
}
```

**Response (已鎖定)**:
```json
{
  "status": "LOCKED",
  "message": "驗證失敗次數過多，請重新發送驗證碼"
}
```

**錯誤碼**:
- `400 BAD_REQUEST`: 驗證碼錯誤
- `403 FORBIDDEN`: 已鎖定（錯誤次數達到 3 次）

---

### 3. 重新發送 OTP

**Endpoint**: `POST /auth/phone/resend-otp/`

**說明**: 重新發送 OTP 驗證碼到指定手機號碼。

**Request Body**:
```json
{
  "phone_number": "+886987654321"
}
```

**參數說明**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| phone_number | string | ✅ | 完整手機號碼（包含國碼） |

**Response (成功)**:
```json
{
  "status": "OTP_RESENT",
  "message": "驗證碼已重新發送",
  "retry_after": 60,
  "note": "前端需使用 Firebase JS SDK 重新發送，並將新的 verificationId 傳給 verify-otp API"
}
```

**Response (頻率限制)**:
```json
{
  "status": "TOO_MANY_REQUESTS",
  "message": "請求過於頻繁，請等待 45 秒後再試",
  "retry_after": 45
}
```

**錯誤碼**:
- `400 BAD_REQUEST`: 手機號碼不符
- `429 TOO_MANY_REQUESTS`: 請求過於頻繁

---

## 🔧 整合到現有專案

如果你已有 Django 專案，可以輕鬆整合此手機驗證模組：

### 步驟 1：複製 phone_auth 模組

```bash
# 將 phone_auth 資料夾複製到你的專案中
cp -r phone_auth /path/to/your/project/
```

### 步驟 2：修改 settings.py

在你的 `settings.py` 中加入以下設定：

```python
# INSTALLED_APPS
INSTALLED_APPS = [
    # ... 其他 apps
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'phone_auth',  # 加入手機驗證 app
]

# MIDDLEWARE
MIDDLEWARE = [
    # ... 其他 middleware
    'corsheaders.middleware.CorsMiddleware',
]

# 如果需要擴展現有 User Model
# 將以下欄位加入你的 User Model 中：
# - phone_number (CharField)
# - phone_verified (BooleanField)
# - otp_attempts (IntegerField)
# - verification_status (CharField)
# - verification_id (CharField)
# - last_otp_sent_at (DateTimeField)

# 或直接使用 CustomUser Model
AUTH_USER_MODEL = 'phone_auth.CustomUser'

# Firebase 設定
FIREBASE_CREDENTIALS_PATH = '/path/to/firebase-service-account.json'

# REST Framework 設定
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### 步驟 3：加入 URL 路由

在你的主 `urls.py` 中：

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他路由
    path('auth/phone/', include('phone_auth.urls')),
]
```

### 步驟 4：執行資料庫遷移

```bash
python manage.py makemigrations phone_auth
python manage.py migrate
```

完成！現在你的專案已整合手機驗證功能。

---

## 💻 前端整合指南

### 使用 Firebase JS SDK（建議）

#### 1. 安裝 Firebase SDK

```bash
npm install firebase
```

#### 2. 初始化 Firebase

```javascript
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  RecaptchaVerifier, 
  signInWithPhoneNumber 
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  // ... 其他配置
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
```

#### 3. 發送 OTP

```javascript
// 設定 reCAPTCHA 驗證器
window.recaptchaVerifier = new RecaptchaVerifier(
  'recaptcha-container',
  {
    'size': 'invisible',
    'callback': (response) => {
      // reCAPTCHA solved
    }
  },
  auth
);

// 發送 OTP
const phoneNumber = '+886987654321';
const appVerifier = window.recaptchaVerifier;

signInWithPhoneNumber(auth, phoneNumber, appVerifier)
  .then((confirmationResult) => {
    // OTP 已發送
    window.confirmationResult = confirmationResult;
    console.log('OTP sent successfully');
    
    // （可選）通知後端 OTP 已發送
    fetch('/auth/phone/send-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token your-auth-token'
      },
      body: JSON.stringify({
        country_code: '+886',
        phone_number: '987654321'
      })
    });
  })
  .catch((error) => {
    console.error('Error sending OTP:', error);
  });
```

#### 4. 驗證 OTP

```javascript
// 使用者輸入 OTP 後
const code = '123456';  // 使用者輸入的驗證碼

window.confirmationResult.confirm(code)
  .then((result) => {
    // 驗證成功（前端），準備呼叫後端完成綁定
    const user = result.user;
    
    // 直接將 verificationId 與 6 位 OTP 傳給後端
    fetch('/auth/phone/verify-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token your-auth-token'
      },
      body: JSON.stringify({
        verification_id: window.confirmationResult.verificationId,
        otp_code: code
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'VERIFIED') {
        console.log('Phone verification successful!');
        // 顯示成功訊息，導向下一頁
      }
    });
  })
  .catch((error) => {
    console.error('Invalid OTP:', error);
    // 顯示錯誤訊息
  });
```

#### 5. 重新發送 OTP

```javascript
// 60 秒後可重新發送
setTimeout(() => {
  // 重新執行步驟 3 的發送 OTP 流程
  signInWithPhoneNumber(auth, phoneNumber, appVerifier)
    .then((confirmationResult) => {
      window.confirmationResult = confirmationResult;
      console.log('OTP resent successfully');
    });
}, 60000);
```

### React 範例

完整的 React 元件範例：

```jsx
import React, { useState } from 'react';
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';

function PhoneVerification() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(1); // 1: 輸入手機, 2: 輸入OTP
  const [confirmationResult, setConfirmationResult] = useState(null);

  const auth = getAuth();

  const sendOTP = async () => {
    // 設定 reCAPTCHA
    window.recaptchaVerifier = new RecaptchaVerifier(
      'recaptcha-container',
      { 'size': 'invisible' },
      auth
    );

    const fullPhone = `+886${phoneNumber}`;
    
    try {
      const result = await signInWithPhoneNumber(
        auth,
        fullPhone,
        window.recaptchaVerifier
      );
      
      setConfirmationResult(result);
      setStep(2);
      alert('驗證碼已發送！');
    } catch (error) {
      console.error('Error:', error);
      alert('發送失敗：' + error.message);
    }
  };

  const verifyOTP = async () => {
    try {
      const result = await confirmationResult.confirm(otp);

      // 傳給後端驗證（verification_id + 6 位 OTP）
      const response = await fetch('/auth/phone/verify-otp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Token your-auth-token'
        },
        body: JSON.stringify({
          verification_id: confirmationResult.verificationId,
          otp_code: otp
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'VERIFIED') {
        alert('驗證成功！');
        // 導向下一頁
      }
    } catch (error) {
      console.error('Error:', error);
      alert('驗證失敗：' + error.message);
    }
  };

  return (
    <div>
      {step === 1 && (
        <div>
          <h2>綁定手機號碼</h2>
          <input
            type="tel"
            placeholder="987654321"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
          />
          <button onClick={sendOTP}>發送驗證碼</button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2>輸入驗證碼</h2>
          <input
            type="text"
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            maxLength="6"
          />
          <button onClick={verifyOTP}>驗證</button>
        </div>
      )}

      <div id="recaptcha-container"></div>
    </div>
  );
}

export default PhoneVerification;
```

---

## 🔍 常見問題

### Q1: Firebase 初始化失敗怎麼辦？

**A**: 請檢查：
1. `firebase-service-account.json` 檔案路徑是否正確
2. 檔案內容是否完整（應為有效的 JSON 格式）
3. Firebase Console 中是否已啟用 Phone Authentication
4. Service Account 是否有足夠的權限

### Q2: 為什麼收不到 SMS？

**A**: 常見原因：
1. **Firebase 專案未啟用計費**：免費方案有限制，可能需要升級到 Blaze 方案
2. **手機號碼格式錯誤**：確保包含正確的國碼（例如：+886987654321）
3. **Firebase Console 限制**：某些地區可能有發送限制
4. **測試環境**：可在 Firebase Console 設定測試手機號碼

### Q3: 如何在測試環境使用？

**A**: 在 Firebase Console 中設定測試手機號碼：
1. 前往 **Authentication** → **Sign-in method** → **Phone**
2. 展開 **Phone numbers for testing**
3. 新增測試號碼與對應的驗證碼（例如：+886987654321 → 123456）
4. 測試號碼不會真正發送 SMS，直接使用設定的驗證碼即可

### Q4: Rate Limiting 如何調整？

**A**: 在 `views.py` 中修改：

```python
# 原本是 60 秒
if time_since_last < timedelta(seconds=60):

# 改為 30 秒
if time_since_last < timedelta(seconds=30):
```

### Q5: 如何自訂錯誤訊息？

**A**: 在 `views.py` 中修改 Response 的 `message` 欄位即可。

### Q6: 支援哪些國家的手機號碼？

**A**: 支援所有 Firebase Phone Auth 支援的國家，包括：
- 🇹🇼 台灣 (+886)
- 🇨🇳 中國 (+86)
- 🇭🇰 香港 (+852)
- 🇺🇸 美國 (+1)
- 🇯🇵 日本 (+81)
- 等...

完整列表請參考 [Firebase 文件](https://firebase.google.com/docs/auth/web/phone-auth)。

### Q7: 如何切換到 PostgreSQL？

**A**: 在 `settings.py` 中修改 `DATABASES` 設定：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

並安裝 PostgreSQL 驅動：
```bash
pip install psycopg2-binary
```

---

## 📝 授權

此專案採用 MIT 授權。

---

## 🎯 下一步建議

1. **安全強化**：
   - 在生產環境啟用 HTTPS
   - 設定更嚴格的 CORS 規則
   - 使用環境變數管理敏感資訊

2. **效能優化**：
   - 使用 Redis 做 Rate Limiting
   - 實作 Cache 機制
   - 資料庫查詢優化

3. **功能擴展**：
   - 支援多個手機號碼綁定
   - 新增手機號碼變更功能
   - 實作手機號碼解綁功能

4. **監控與分析**：
   - 整合 Sentry 錯誤追蹤
   - 新增 Analytics 統計
   - 設定告警通知

