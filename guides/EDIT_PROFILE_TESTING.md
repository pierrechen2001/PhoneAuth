# 個人資料編輯 API 測試指南

## 前置準備

1. 確保 Django 伺服器已啟動：
```bash
python manage.py runserver
```

2. 建立資料庫遷移：
```bash
python manage.py makemigrations
python manage.py migrate
```

3. 建立測試使用者（選擇性）：
```bash
python manage.py createsuperuser
```

---

## 測試工具

### 使用 cURL

#### 1. 獲取個人資料

```bash
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

#### 2. 更新個人資料

```bash
curl -X PATCH http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Pierre Huang",
    "gender": "M",
    "age": "25",
    "degree": "Master",
    "motivation_1": "幫助他人",
    "motivation_2": "自我成長",
    "motivation_3": "獲得經驗"
  }'
```

#### 3. 上傳頭像

```bash
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "avatar=@/path/to/profile_pic.jpg"
```

#### 4. 刪除頭像

```bash
curl -X DELETE http://localhost:8000/api/user/avatar/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

### 使用 Python Requests

```python
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. 獲取個人資料
response = requests.get(
    f"{BASE_URL}/api/user/profile/",
    headers=headers
)
print("Get Profile:", response.json())

# 2. 更新個人資料
data = {
    "nickname": "Pierre Huang",
    "gender": "M",
    "age": "25",
    "degree": "Master"
}
response = requests.patch(
    f"{BASE_URL}/api/user/profile/",
    headers=headers,
    json=data
)
print("Update Profile:", response.json())

# 3. 上傳頭像
files = {
    "avatar": open("/path/to/profile_pic.jpg", "rb")
}
response = requests.post(
    f"{BASE_URL}/api/user/avatar/upload/",
    headers={"Authorization": f"Bearer {TOKEN}"},
    files=files
)
print("Upload Avatar:", response.json())

# 4. 刪除頭像
response = requests.delete(
    f"{BASE_URL}/api/user/avatar/",
    headers=headers
)
print("Delete Avatar:", response.json())
```

---

### 使用 Django 測試框架

```bash
# 執行所有測試
python manage.py test edit_profile

# 執行特定測試
python manage.py test edit_profile.tests.ProfileUpdateTest

# 詳細輸出
python manage.py test edit_profile -v 2
```

---

## 完整測試場景

### 場景1：完整的個人資料編輯流程

```bash
# 步驟1：取得目前資料
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# 步驟2：更新部分資料
curl -X PATCH http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "New Nickname",
    "age": "30"
  }'

# 步驟3：驗證更新成功
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### 場景2：頭像上傳和刪除

```bash
# 步驟1：上傳頭像
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "avatar=@avatar.jpg"

# 步驟2：查看上傳後的資料
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 步驟3：刪除頭像
curl -X DELETE http://localhost:8000/api/user/avatar/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 步驟4：驗證刪除成功
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 預期結果

### 成功更新個人資料

**Request:**
```json
{
  "nickname": "Pierre",
  "gender": "M",
  "age": "23"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "個人資料更新成功",
  "data": {
    "id": 1,
    "username": "pierre",
    "email": "pierre@example.com",
    "nickname": "Pierre",
    "gender": "M",
    "age": "23",
    "degree": "",
    "motivation_1": null,
    "motivation_2": null,
    "motivation_3": null,
    "phone_number": "+886987654321",
    "phone_verified": true
  }
}
```

### 成功上傳頭像

**Response (200):**
```json
{
  "success": true,
  "message": "頭像上傳成功",
  "data": {
    "id": 1,
    "avatar_url": "http://localhost:8000/media/avatars/2024/11/18/avatar.jpg",
    "avatar_uploaded_at": "2024-11-18T10:30:45.123456Z"
  }
}
```

---

## 常見錯誤和解決方案

### 1. 401 Unauthorized

**原因：** 未提供認證令牌或令牌無效

**解決方案：**
```bash
# 確保在 Authorization header 中提供有效的 token
-H "Authorization: Bearer YOUR_VALID_TOKEN"
```

### 2. 400 Bad Request

**原因：** 請求數據格式不正確或欄位超過最大長度

**解決方案：**
- 檢查 JSON 格式是否正確
- 檢查欄位長度是否超過限制
- 參考 API 規格確認支援的欄位

### 3. 413 Payload Too Large

**原因：** 上傳的圖片檔案過大（> 5MB）

**解決方案：**
```bash
# 壓縮圖片或使用更小的檔案
# 使用線上工具如 TinyPNG 或 ImageOptim 等
```

### 4. 415 Unsupported Media Type

**原因：** 上傳的檔案不是有效的圖片格式

**解決方案：**
- 確保檔案是 JPG、PNG 或 GIF 格式
- 檢查檔案副檔名是否正確

### 5. 500 Internal Server Error

**原因：** 伺服器內部錯誤

**解決方案：**
- 檢查 Django 伺服器的日誌輸出
- 確保資料庫遷移已完成
- 重啟 Django 伺服器

---

## 性能測試

### 使用 Apache Bench

```bash
# 測試獲取個人資料的性能（100 個請求）
ab -n 100 -c 10 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/user/profile/
```

### 使用 Locust

```bash
# 建立 locustfile.py
from locust import HttpUser, task

class UserProfileTests(HttpUser):
    @task
    def get_profile(self):
        self.client.get("/api/user/profile/")
    
    @task
    def update_profile(self):
        self.client.patch("/api/user/profile/", json={
            "nickname": "Test User"
        })

# 執行 Locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## 調試技巧

### 1. 查看詳細的 API 文件

訪問 Swagger UI：
```
http://localhost:8000/api/docs/
```

或 ReDoc：
```
http://localhost:8000/api/redoc/
```

### 2. 查看 Django 日誌

```bash
# 在 settings.py 中啟用詳細日誌
LOGGING = {
    'loggers': {
        'edit_profile': {
            'level': 'DEBUG',
        },
    },
}
```

### 3. 使用 Django Debug Toolbar

```bash
pip install django-debug-toolbar
```

然後在 settings.py 中配置...

### 4. 使用 Python 的 ipdb 調試

```python
# 在 views.py 中添加
import ipdb; ipdb.set_trace()
```

---

## 驗證清單

- [ ] 已執行資料庫遷移
- [ ] Django 伺服器已啟動
- [ ] 可以獲取個人資料
- [ ] 可以更新個人資料
- [ ] 可以上傳頭像
- [ ] 可以刪除頭像
- [ ] 所有錯誤情況都返回正確的狀態碼
- [ ] 未授權使用者無法訪問 API
- [ ] 超大檔案被拒絕
- [ ] 無效的圖片格式被拒絕

---

## 相關文件

- [個人資料編輯 API 規格](./EDIT_PROFILE_API_SPEC.md)
- [Phone Authentication API 測試指南](./API_TESTING_GUIDE.md)
- [快速開始指南](./QUICK_START.md)

