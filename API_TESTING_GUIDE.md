# API 測試指南

本文件提供使用 cURL、Postman 和 Python 測試 API 的範例。

## 前置準備

1. 確保伺服器正在運行：
```bash
python manage.py runserver
```

2. 確保你已登入並取得認證 Token

## 使用 cURL 測試

### 1. 發送 OTP

```bash
curl -X POST http://127.0.0.1:8000/auth/phone/send-otp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -d '{
    "country_code": "+886",
    "phone_number": "987654321"
  }'
```

### 2. 驗證 OTP（使用 ID Token）

```bash
curl -X POST http://127.0.0.1:8000/auth/phone/verify-otp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -d '{
    "id_token": "eyJhbGciOiJSUzI1NiIs..."
  }'
```

### 3. 重新發送 OTP

```bash
curl -X POST http://127.0.0.1:8000/auth/phone/resend-otp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -d '{
    "phone_number": "+886987654321"
  }'
```

## 使用 Python requests 測試

```python
import requests

# 設定
BASE_URL = "http://127.0.0.1:8000"
AUTH_TOKEN = "YOUR_AUTH_TOKEN"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {AUTH_TOKEN}"
}

# 1. 發送 OTP
response = requests.post(
    f"{BASE_URL}/auth/phone/send-otp/",
    headers=HEADERS,
    json={
        "country_code": "+886",
        "phone_number": "987654321"
    }
)
print("發送 OTP 回應：", response.json())

# 2. 驗證 OTP
response = requests.post(
    f"{BASE_URL}/auth/phone/verify-otp/",
    headers=HEADERS,
    json={
        "id_token": "eyJhbGciOiJSUzI1NiIs..."
    }
)
print("驗證 OTP 回應：", response.json())

# 3. 重新發送 OTP
response = requests.post(
    f"{BASE_URL}/auth/phone/resend-otp/",
    headers=HEADERS,
    json={
        "phone_number": "+886987654321"
    }
)
print("重新發送 OTP 回應：", response.json())
```

## 使用 Postman 測試

### 設定環境變數

在 Postman 中建立以下環境變數：

- `base_url`: `http://127.0.0.1:8000`
- `auth_token`: `YOUR_AUTH_TOKEN`

### Collection 設定

1. **發送 OTP**
   - Method: `POST`
   - URL: `{{base_url}}/auth/phone/send-otp/`
   - Headers:
     - `Content-Type`: `application/json`
     - `Authorization`: `Token {{auth_token}}`
   - Body (raw JSON):
     ```json
     {
       "country_code": "+886",
       "phone_number": "987654321"
     }
     ```

2. **驗證 OTP**
   - Method: `POST`
   - URL: `{{base_url}}/auth/phone/verify-otp/`
   - Headers:
     - `Content-Type`: `application/json`
     - `Authorization`: `Token {{auth_token}}`
   - Body (raw JSON):
     ```json
     {
       "id_token": "eyJhbGciOiJSUzI1NiIs..."
     }
     ```

3. **重新發送 OTP**
   - Method: `POST`
   - URL: `{{base_url}}/auth/phone/resend-otp/`
   - Headers:
     - `Content-Type`: `application/json`
     - `Authorization`: `Token {{auth_token}}`
   - Body (raw JSON):
     ```json
     {
       "phone_number": "+886987654321"
     }
     ```

## 測試流程建議

### 完整測試流程

1. **正常流程測試**
   - 發送 OTP → 收到成功回應
   - 驗證 OTP（正確的驗證碼）→ 驗證成功
   - 檢查使用者資料是否已更新

2. **錯誤處理測試**
   - 發送 OTP 後立即再次發送 → 應收到 `TOO_MANY_REQUESTS`
   - 驗證時輸入錯誤的驗證碼 → 應顯示剩餘次數
   - 連續輸入錯誤 3 次 → 應被鎖定（`LOCKED`）

3. **Rate Limiting 測試**
   - 60 秒內重複發送 OTP → 應被限制
   - 等待 60 秒後再試 → 應可正常發送

4. **邊界測試**
   - 測試各種手機號碼格式
   - 測試各種國碼
   - 測試特殊字元輸入

## 預期回應範例

### 成功回應

```json
{
  "status": "OTP_SENT",
  "message": "驗證碼已發送到您的手機",
  "expires_in": 300
}
```

### 錯誤回應

```json
{
  "error": "VALIDATION_ERROR",
  "message": "輸入資料格式錯誤",
  "details": {
    "phone_number": ["手機號碼格式錯誤"]
  }
}
```

## 常見問題排查

### 401 Unauthorized
- 檢查 Token 是否正確
- 檢查 Token 是否已過期
- 確認 Header 格式：`Authorization: Token YOUR_TOKEN`

### 400 Bad Request
- 檢查 Request Body 格式是否正確
- 檢查必填欄位是否都有提供
- 查看 `details` 欄位了解具體錯誤

### 429 Too Many Requests
- 等待 60 秒後再試
- 查看 `retry_after` 欄位了解需等待的秒數

### 500 Internal Server Error
- 檢查伺服器日誌：`logs/phone_auth.log`
- 檢查 Firebase 設定是否正確
- 確認資料庫連線正常

