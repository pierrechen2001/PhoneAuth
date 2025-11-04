# 快速開始指南

10 分鐘內完成手機驗證 API 的設定與測試！

## ⚡️ 5 步驟快速啟動

### 步驟 1：安裝依賴 (1 分鐘)

```bash
# 建立並啟動虛擬環境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 安裝套件
pip install -r requirements.txt
```

### 步驟 2：Firebase 設定 (3 分鐘)

1. **前往 Firebase Console**: https://console.firebase.google.com/
2. **選擇專案** 或 **建立新專案**
3. **啟用 Phone Authentication**:
   - Authentication → Sign-in method → Phone → 啟用
4. **下載 Service Account**:
   - Project Settings → Service accounts → Generate new private key
   - 下載 JSON，重新命名為 `firebase-service-account.json`
   - 放在專案根目錄

### 步驟 3：環境設定 (1 分鐘)

建立 `.env` 檔案：

```bash
cat > .env << 'EOF'
SECRET_KEY=django-insecure-dev-key-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
EOF
```

### 步驟 4：資料庫初始化 (2 分鐘)

```bash
# 執行遷移
python manage.py migrate

# 建立超級使用者（用於登入）
python manage.py createsuperuser
# 輸入：username, email（可選）, password
```

### 步驟 5：啟動伺服器 (1 分鐘)

```bash
python manage.py runserver
```

✅ **完成！** 現在你可以存取：

- **API 文件**: http://127.0.0.1:8000/api/docs/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **API 端點**: http://127.0.0.1:8000/auth/phone/

---

## 🧪 快速測試

### 方法 1：使用瀏覽器（最簡單）

1. 開啟 http://127.0.0.1:8000/api/docs/
2. 點擊 **Authorize** 按鈕，登入
3. 展開 API 端點，點擊 **Try it out**
4. 輸入測試資料，點擊 **Execute**

### 方法 2：使用 cURL

```bash
# 先取得認證 Token（假設你建立了使用者 testuser）
# 或使用 Django Admin 登入後的 Session

# 測試發送 OTP
curl -X POST http://127.0.0.1:8000/auth/phone/send-otp/ \
  -H "Content-Type: application/json" \
  -u testuser:password \
  -d '{
    "country_code": "+886",
    "phone_number": "987654321"
  }'
```

### 方法 3：使用測試手機號碼（不需真的發 SMS）

1. 前往 Firebase Console
2. Authentication → Sign-in method → Phone → Phone numbers for testing
3. 新增測試號碼，例如：
   - Phone number: `+886987654321`
   - Code: `123456`
4. 使用這個號碼測試，不會真的發送 SMS

---

## 📁 專案結構說明

```
PhoneOath/
├── config/              ← Django 設定
├── phone_auth/          ← 手機驗證模組（核心）
│   ├── models.py       ← 資料模型
│   ├── views.py        ← API 邏輯
│   ├── serializers.py  ← API 格式定義
│   └── firebase_service.py  ← Firebase 整合
├── manage.py            ← Django 指令工具
└── requirements.txt     ← 依賴套件
```

---

## 🎯 常用指令

```bash
# 啟動開發伺服器
python manage.py runserver

# 執行資料庫遷移
python manage.py migrate

# 建立超級使用者
python manage.py createsuperuser

# 開啟 Python Shell
python manage.py shell

# 檢查專案設定
python manage.py check

# 查看所有 URL
python manage.py show_urls  # 需安裝 django-extensions
```

---

## 🔍 驗證安裝是否成功

### 檢查清單

- [ ] ✅ 可以存取 http://127.0.0.1:8000/api/docs/
- [ ] ✅ 可以登入 Django Admin
- [ ] ✅ API 文件顯示 3 個端點：
  - POST /auth/phone/send-otp/
  - POST /auth/phone/verify-otp/
  - POST /auth/phone/resend-otp/
- [ ] ✅ 沒有錯誤訊息在終端機

---

## ⚠️ 常見問題快速解決

### 問題 1：ImportError: No module named 'rest_framework'

**解決方式**:
```bash
pip install -r requirements.txt
```

### 問題 2：Firebase 初始化失敗

**解決方式**:
- 確認 `firebase-service-account.json` 在專案根目錄
- 確認檔案格式正確（有效的 JSON）
- 檢查 `.env` 中的 `FIREBASE_CREDENTIALS_PATH`

### 問題 3：資料庫錯誤

**解決方式**:
```bash
# 刪除舊的資料庫（開發環境）
rm db.sqlite3
rm -rf phone_auth/migrations/

# 重新建立
python manage.py makemigrations phone_auth
python manage.py migrate
```

### 問題 4：Cannot import name 'CustomUser'

**解決方式**:
- 確認 `AUTH_USER_MODEL = 'phone_auth.CustomUser'` 在 settings.py 中
- 執行 `python manage.py migrate`

---

## 🎓 下一步學習

1. **閱讀完整文件**: 
   - [README.md](README.md) - 完整說明
   - [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) - 測試指南
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南

2. **整合前端**:
   - 查看 README.md 中的「前端整合指南」
   - 使用 Firebase JS SDK 完成前端整合

3. **自訂功能**:
   - 修改 `views.py` 調整業務邏輯
   - 修改 `models.py` 新增欄位
   - 修改 `serializers.py` 調整 API 格式

---

## 💡 小技巧

### 快速測試腳本

建立 `test_api.py`：

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 使用基本認證
auth = ('testuser', 'password')

# 測試發送 OTP
response = requests.post(
    f"{BASE_URL}/auth/phone/send-otp/",
    auth=auth,
    json={
        "country_code": "+886",
        "phone_number": "987654321"
    }
)

print("Status:", response.status_code)
print("Response:", response.json())
```

執行：
```bash
python test_api.py
```

---

## 📞 需要幫助？

- **完整文件**: [README.md](README.md)
- **API 測試**: [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)
- **部署說明**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API 規格**: [api_spec.md](api_spec.md)

---

**開始建立你的手機驗證功能吧！🎉**

