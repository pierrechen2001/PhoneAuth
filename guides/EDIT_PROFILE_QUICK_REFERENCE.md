# 個人資料編輯 API 快速參考

## 快速開始

```bash
# 1. 執行遷移
python manage.py makemigrations
python manage.py migrate

# 2. 建立媒體目錄
mkdir -p media/avatars

# 3. 啟動伺服器
python manage.py runserver
```

---

## API 端點快速查詢

### 獲取個人資料 (GET)
```
GET /api/user/profile/

Response (200):
{
  "success": true,
  "message": "個人資料獲取成功",
  "data": { ... }
}
```

### 更新個人資料 (PATCH)
```
PATCH /api/user/profile/

Request:
{
  "nickname": "Pierre",
  "gender": "M",
  "age": "23",
  "degree": "Bachelor"
}

Response (200):
{
  "success": true,
  "message": "個人資料更新成功",
  "data": { ... }
}
```

### 上傳頭像 (POST)
```
POST /api/user/avatar/upload/

Form Data:
- avatar: <image_file>

Response (200):
{
  "success": true,
  "message": "頭像上傳成功",
  "data": {
    "id": 1,
    "avatar_url": "/media/avatars/...",
    "avatar_uploaded_at": "2024-11-18T..."
  }
}
```

### 刪除頭像 (DELETE)
```
DELETE /api/user/avatar/

Response (200):
{
  "success": true,
  "message": "頭像刪除成功"
}
```

---

## cURL 範本

### 獲取個人資料
```bash
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"
```

### 更新個人資料
```bash
curl -X PATCH http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname": "Pierre", "gender": "M"}'
```

### 上傳頭像
```bash
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -H "Authorization: Bearer TOKEN" \
  -F "avatar=@image.jpg"
```

### 刪除頭像
```bash
curl -X DELETE http://localhost:8000/api/user/avatar/ \
  -H "Authorization: Bearer TOKEN"
```

---

## Python 範本

```python
import requests

TOKEN = "your_token_here"
BASE = "http://localhost:8000"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 獲取
r = requests.get(f"{BASE}/api/user/profile/", headers=HEADERS)
print(r.json())

# 更新
data = {"nickname": "Pierre", "age": "25"}
r = requests.patch(f"{BASE}/api/user/profile/", 
                   json=data, headers=HEADERS)
print(r.json())

# 上傳
files = {"avatar": open("pic.jpg", "rb")}
r = requests.post(f"{BASE}/api/user/avatar/upload/", 
                  files=files, headers=HEADERS)
print(r.json())

# 刪除
r = requests.delete(f"{BASE}/api/user/avatar/", headers=HEADERS)
print(r.json())
```

---

## 欄位大小限制

| 欄位 | 最大長度 | 範例 |
|-----|---------|------|
| nickname | 150 | "Pierre Huang" |
| gender | 1 | "M" / "F" / "O" |
| age | 10 | "25" |
| degree | 20 | "Bachelor" |
| motivation_1/2/3 | 100 | "助人成長" |
| avatar | 5MB | image.jpg |

---

## 錯誤狀態碼

| 狀態碼 | 原因 |
|------|------|
| 200 | 成功 ✓ |
| 400 | 驗證失敗或檔案過大 ✗ |
| 401 | 未授權 ✗ |
| 500 | 伺服器錯誤 ✗ |

---

## 常用命令

```bash
# 執行全部測試
python manage.py test edit_profile

# 執行特定測試
python manage.py test edit_profile.tests.ProfileUpdateTest

# 進入 Django Shell
python manage.py shell
>>> from phone_auth.models import CustomUser
>>> user = CustomUser.objects.first()
>>> print(user.nickname)

# 建立超級用戶
python manage.py createsuperuser

# 查看數據庫遷移狀態
python manage.py showmigrations
```

---

## 目錄結構

```
edit_profile/
├── __init__.py
├── apps.py          # 應用配置
├── models.py        # 資料模型
├── views.py         # API 端點
├── serializers.py   # 數據驗證
├── urls.py          # 路由
├── admin.py         # Admin 配置
└── tests.py         # 測試

media/
└── avatars/         # 上傳的頭像
    └── YYYY/MM/DD/  # 按日期組織
```

---

## 文件位置

| 檔案 | 位置 |
|-----|------|
| API 規格 | `/guides/EDIT_PROFILE_API_SPEC.md` |
| 測試指南 | `/guides/EDIT_PROFILE_TESTING.md` |
| 設定指南 | `/guides/EDIT_PROFILE_SETUP.md` |
| 本文件 | `/guides/EDIT_PROFILE_QUICK_REFERENCE.md` |

---

## 前端集成核心代碼

```javascript
// React Hook
const useProfile = (token) => {
  const [profile, setProfile] = useState(null);
  
  const getProfile = async () => {
    const res = await fetch('/api/user/profile/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    setProfile((await res.json()).data);
  };
  
  const updateProfile = async (data) => {
    await fetch('/api/user/profile/', {
      method: 'PATCH',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
  };
  
  const uploadAvatar = async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    await fetch('/api/user/avatar/upload/', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
  };
  
  return { profile, getProfile, updateProfile, uploadAvatar };
};
```

---

## 故障排除

| 問題 | 解決方案 |
|-----|---------|
| 401 Unauthorized | 檢查 Authorization header 和 token 有效性 |
| 413 Payload Too Large | 減小圖片尺寸（< 5MB） |
| 415 Unsupported Media Type | 確保上傳的是有效的圖片格式 |
| No module named 'PIL' | `pip install Pillow` |
| media 目錄不存在 | `mkdir -p media/avatars` |

---

## 相關資源

- [完整 API 規格](./EDIT_PROFILE_API_SPEC.md)
- [詳細測試指南](./EDIT_PROFILE_TESTING.md)
- [安裝配置指南](./EDIT_PROFILE_SETUP.md)
- [Phone Auth API](./API_TESTING_GUIDE.md)

