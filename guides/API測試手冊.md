# Phone Auth API 測試手冊

> 📅 更新日期：2025年12月1日  
> 🎯 測試環境：https://ai.akira-dialog.com/auth/phone/

## 📋 目錄

1. [前置準備](#前置準備)
2. [測試流程](#測試流程)
3. [API 端點測試](#api-端點測試)
4. [常見問題](#常見問題)
5. [錯誤情境測試](#錯誤情境測試)

---

## 前置準備

### 1. 登入取得 Session

所有 API 都需要先登入才能使用。測試前請先：

```bash
# 方式一：使用瀏覽器登入 Django Admin
https://ai.akira-dialog.com/admin/

# 方式二：使用 Session Authentication
# 登入後瀏覽器會自動儲存 session cookie
```

### 2. Firebase JS SDK 設定（前端）

```javascript
// Firebase 設定
import { initializeApp } from 'firebase/app';
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
```

### 3. 測試工具

- **Postman** 或 **Insomnia**（用於測試 API）
- **瀏覽器開發者工具**（用於前端 Firebase 測試）

---

## 測試流程

### 完整流程圖

```
1. 前端：使用 Firebase JS SDK 發送 OTP
   ↓
2. 使用者：收到 SMS 驗證碼
   ↓
3. 前端：使用者輸入驗證碼，呼叫 Firebase confirm()
   ↓
4. 前端：成功後取得 idToken
   ↓
5. 後端：呼叫 verify-otp API 驗證 idToken
   ↓
6. 完成：手機號碼綁定成功
```

### 推薦測試方式

#### 方式 A：純前端 Firebase（推薦）

**不需要呼叫 send-otp API**，直接在前端完成：

```javascript
// 1. 設定 reCAPTCHA
window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
  'size': 'invisible'
});

// 2. 發送 OTP
const phoneNumber = '+886987654321';
const appVerifier = window.recaptchaVerifier;

signInWithPhoneNumber(auth, phoneNumber, appVerifier)
  .then((confirmationResult) => {
    // 儲存 confirmationResult，等待使用者輸入 OTP
    window.confirmationResult = confirmationResult;
    console.log('OTP 已發送');
  })
  .catch((error) => {
    console.error('發送失敗：', error);
  });

// 3. 驗證 OTP
const otpCode = '123456'; // 使用者輸入
window.confirmationResult.confirm(otpCode)
  .then(async (result) => {
    // 取得 idToken
    const idToken = await result.user.getIdToken();
    
    // 4. 呼叫後端 API
    const response = await fetch('https://ai.akira-dialog.com/auth/phone/verify-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Session Authentication 會自動帶 cookie
      },
      credentials: 'include',
      body: JSON.stringify({
        verification_id: idToken,  // 使用 idToken
        otp_code: otpCode
      })
    });
    
    const data = await response.json();
    console.log('後端驗證結果：', data);
  })
  .catch((error) => {
    console.error('驗證失敗：', error);
  });
```

#### 方式 B：搭配後端 API（可選）

如果想讓後端記錄狀態：

```javascript
// 1. 呼叫後端 send-otp（記錄狀態）
await fetch('https://ai.akira-dialog.com/auth/phone/send-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    country_code: '+886',
    phone_number: '987654321'
  })
});

// 2. 使用 Firebase JS SDK 發送（實際發送）
const confirmationResult = await signInWithPhoneNumber(auth, '+886987654321', appVerifier);

// 3-4. 同方式 A
```

---

## API 端點測試

### 1️⃣ Send OTP（可選）

**端點：** `POST /auth/phone/send-otp/`

**Request Body:**
```json
{
  "country_code": "+886",
  "phone_number": "987654321"
}
```

**成功回應（200 OK）：**
```json
{
  "status": "OTP_SENT",
  "message": "驗證碼已發送到您的手機，請在前端完成 Firebase Phone Auth 流程",
  "expires_in": 300,
  "note": "前端需使用 Firebase JS SDK 的 signInWithPhoneNumber 方法，並將返回的 verificationId 傳給 verify-otp API"
}
```

**錯誤回應（429 Too Many Requests）：**
```json
{
  "status": "TOO_MANY_REQUESTS",
  "message": "請求過於頻繁，請等待 45 秒後再試",
  "retry_after": 45
}
```

**錯誤回應（400 Bad Request）：**
```json
{
  "error": "PHONE_ALREADY_BOUND",
  "message": "此手機號碼已被其他帳號綁定"
}
```

---

### 2️⃣ Verify OTP（必須）

**端點：** `POST /auth/phone/verify-otp/`

**Request Body:**
```json
{
  "verification_id": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ij...",  // Firebase idToken
  "otp_code": "123456"
}
```

**成功回應（200 OK）：**
```json
{
  "status": "VERIFIED",
  "phone_number": "+886987654321",
  "message": "手機號碼驗證成功"
}
```

**錯誤回應（400 Bad Request - OTP 錯誤）：**
```json
{
  "status": "INVALID_OTP",
  "remaining_attempts": 2,
  "message": "驗證碼錯誤，您還有 2 次機會"
}
```

**錯誤回應（403 Forbidden - 已鎖定）：**
```json
{
  "status": "LOCKED",
  "message": "驗證失敗次數過多，請 60 秒後重新發送驗證碼",
  "retry_after": 60
}
```

---

### 3️⃣ Resend OTP

**端點：** `POST /auth/phone/resend-otp/`

**Request Body:**
```json
{
  "phone_number": "+886987654321"
}
```

**注意：** `resend-otp` 的格式是**完整手機號碼**，不像 `send-otp` 是分開的。

**成功回應（200 OK）：**
```json
{
  "status": "OTP_RESENT",
  "message": "驗證碼已重新發送",
  "retry_after": 60,
  "note": "前端需使用 Firebase JS SDK 重新發送，並將新的 verificationId 傳給 verify-otp API"
}
```

**錯誤回應（429 Too Many Requests）：**
```json
{
  "status": "TOO_MANY_REQUESTS",
  "message": "請求過於頻繁，請等待 30 秒後再試",
  "retry_after": 30
}
```

---

## 常見問題

### Q1: 後端收到的手機號碼是 None？

**A:** 檢查 payload 格式：

❌ **錯誤：**
```json
{
  "phone_number": "+886987654321"
}
```

✅ **正確（send-otp）：**
```json
{
  "country_code": "+886",
  "phone_number": "987654321"
}
```

✅ **正確（resend-otp）：**
```json
{
  "phone_number": "+886987654321"
}
```

### Q2: verify-otp 任意輸入都會過？

**A:** 已修正！現在會真實驗證 Firebase idToken。請確保：
1. `verification_id` 是前端 Firebase 驗證成功後取得的 `idToken`
2. 不是隨便的字串或 Firebase 的 `verificationId`

### Q3: 如何重複測試？

**方法一：** 請管理員在 Django Admin 重置你的使用者狀態：
- `phone_verified` → `False`
- `otp_attempts` → `0`
- `verification_status` → `null`

**方法二：** 使用不同的手機號碼測試

**方法三：** 呼叫 `resend-otp` 會重置嘗試次數

### Q4: Firebase 前端驗證失敗？

**常見原因：**
1. **reCAPTCHA 沒設定**：需要在前端設定 RecaptchaVerifier
2. **測試手機號碼沒加入白名單**：去 Firebase Console → Authentication → Sign-in method → Phone → 加入測試號碼
3. **Firebase 設定錯誤**：檢查 apiKey、authDomain 是否正確

### Q5: LOCKED 狀態怎麼解除？

**兩種方式：**
1. 等待 60 秒後呼叫 `resend-otp`
2. 請管理員在後台重置

---

## 錯誤情境測試

### 測試 1：錯誤次數限制

```javascript
// 1. 發送 OTP
// 2. 故意輸入錯誤的 OTP 3 次
await verifyOTP('fake-token', '111111'); // 第 1 次
await verifyOTP('fake-token', '222222'); // 第 2 次
await verifyOTP('fake-token', '333333'); // 第 3 次 -> LOCKED

// 3. 再次嘗試
await verifyOTP('fake-token', '444444'); // 回應：LOCKED, retry_after: 60
```

### 測試 2：Rate Limiting

```javascript
// 1. 發送 OTP
await sendOTP('+886', '987654321'); // 成功

// 2. 立即再次發送
await sendOTP('+886', '987654321'); // 回應：TOO_MANY_REQUESTS

// 3. 等待 60 秒後再試
setTimeout(() => {
  await sendOTP('+886', '987654321'); // 成功
}, 60000);
```

### 測試 3：手機號碼已被綁定

```javascript
// 1. 使用者 A 綁定 +886987654321
// 2. 使用者 B 嘗試綁定同號碼
await sendOTP('+886', '987654321'); // 回應：PHONE_ALREADY_BOUND
```

---

## Postman 測試範例

### 設定 Cookie（Session Authentication）

1. 先用瀏覽器登入 Django Admin：`https://ai.akira-dialog.com/admin/`
2. 開啟開發者工具 → Application → Cookies
3. 複製 `sessionid` 和 `csrftoken`
4. 在 Postman 的 Headers 加入：

```
Cookie: sessionid=YOUR_SESSION_ID; csrftoken=YOUR_CSRF_TOKEN
X-CSRFToken: YOUR_CSRF_TOKEN
Content-Type: application/json
```

### Send OTP 範例

```bash
curl -X POST https://ai.akira-dialog.com/auth/phone/send-otp/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "country_code": "+886",
    "phone_number": "987654321"
  }'
```

### Verify OTP 範例

```bash
curl -X POST https://ai.akira-dialog.com/auth/phone/verify-otp/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "verification_id": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ij...",
    "otp_code": "123456"
  }'
```

---

## 測試清單 ✅

### 正常流程
- [ ] 使用 Firebase JS SDK 發送 OTP
- [ ] 收到 SMS 驗證碼
- [ ] 前端驗證成功取得 idToken
- [ ] 呼叫後端 verify-otp API
- [ ] 驗證成功，手機號碼綁定

### 錯誤處理
- [ ] 輸入錯誤 OTP 3 次後被鎖定
- [ ] LOCKED 狀態有顯示 retry_after: 60
- [ ] 60 秒內重複發送會被限制
- [ ] 手機號碼已綁定時會拒絕
- [ ] 無效的 idToken 會被拒絕

### 邊界條件
- [ ] 使用不同國碼測試（+1, +86, +886）
- [ ] 手機號碼格式驗證（過短、過長）
- [ ] 未登入時呼叫 API 會被拒絕

---

## 聯絡資訊

如有問題，請聯絡：
- **後端開發**：冠宇（@guanyuchen）
- **專案負責人**：Jeffrey Chen

