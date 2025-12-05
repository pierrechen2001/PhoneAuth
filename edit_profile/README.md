# 個人資料編輯模組 (Edit Profile Module)

## 模組概述

`edit_profile` 是一個 Django 應用程式，提供使用者個人資料編輯和頭像管理的 API 端點。它與 `phone_auth` 應用程式協作，擴展了 `CustomUser` 模型的功能。

## 功能特性

✅ **個人資料管理**
- 獲取使用者完整個人資料
- 編輯個人資料欄位（暱稱、性別、年齡、學歷等）
- 支援多個動機欄位

✅ **頭像管理**
- 上傳使用者頭像
- 自動檔案驗證和大小限制（5MB）
- 刪除頭像

✅ **安全性**
- 所有 API 端點均需登入
- 使用者只能編輯自己的資料
- 完整的輸入驗證

✅ **完整文檔**
- OpenAPI/Swagger 集成
- 詳細的 API 規格文件
- 測試指南和範例代碼

## 快速開始

### 1. 安裝

```bash
# 確保 Pillow 已安裝（用於圖片處理）
pip install Pillow

# 執行遷移
python manage.py makemigrations
python manage.py migrate

# 建立媒體目錄
mkdir -p media/avatars
```

### 2. 使用

```bash
# 啟動伺服器
python manage.py runserver

# 訪問 API 文件
http://localhost:8000/api/docs/
```

### 3. 基本 API 調用

```bash
# 獲取個人資料
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 更新個人資料
curl -X PATCH http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname": "Pierre"}'

# 上傳頭像
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "avatar=@image.jpg"
```

## API 端點

| 方法 | 端點 | 功能 |
|-----|------|------|
| GET | `/api/user/profile/` | 獲取個人資料 |
| PATCH | `/api/user/profile/` | 更新個人資料 |
| POST | `/api/user/avatar/upload/` | 上傳頭像 |
| DELETE | `/api/user/avatar/` | 刪除頭像 |

更詳細的端點說明，見 [API 規格文件](../../guides/EDIT_PROFILE_API_SPEC.md)

## 目錄結構

```
edit_profile/
├── __init__.py           # 模組初始化
├── apps.py               # 應用程式配置
├── models.py             # 資料模型（預留）
├── views.py              # API 端點實現
├── serializers.py        # 數據序列化和驗證
├── urls.py               # URL 路由
├── admin.py              # Django Admin 配置
├── tests.py              # 單位測試
└── README.md             # 本文件
```

## 主要文件說明

### views.py

定義了四個主要 API 端點：

- **`profile_view(request)`** - GET/PATCH 端點，獲取或更新使用者個人資料（共用同一路徑）
- **`upload_avatar(request)`** - POST 端點，上傳使用者頭像
- **`delete_avatar(request)`** - DELETE 端點，刪除使用者頭像

### serializers.py

定義了 API 的序列化器：

- **`UpdateProfileSerializer`** - 驗證個人資料更新請求
- **`ProfileResponseSerializer`** - 序列化個人資料回應
- **`AvatarUploadSerializer`** - 驗證頭像上傳請求
- **`AvatarResponseSerializer`** - 序列化頭像上傳回應

### urls.py

定義了模組的 URL 路由：

```python
urlpatterns = [
    path('profile/', views.profile_view, name='profile'),  # GET 和 PATCH 共用同一路徑
    path('avatar/upload/', views.upload_avatar, name='upload_avatar'),
    path('avatar/', views.delete_avatar, name='delete_avatar'),
]
```

## 支援的個人資料欄位

| 欄位 | 類型 | 最大長度 | 可為空 | 說明 |
|-----|------|---------|-------|------|
| nickname | CharField | 150 | Yes | 暱稱 |
| gender | CharField | 1 | Yes | 性別 |
| age | CharField | 10 | Yes | 年齡 |
| degree | CharField | 20 | Yes | 學歷 |
| motivation_1 | CharField | 100 | Yes | 動機1 |
| motivation_2 | CharField | 100 | Yes | 動機2 |
| motivation_3 | CharField | 100 | Yes | 動機3 |
| phone_number | CharField | 20 | Yes | 手機號碼 |
| phone_verified | BooleanField | - | No | 手機驗證狀態 |

## 響應格式

所有成功的 API 回應都遵循以下格式：

```json
{
  "success": true,
  "message": "操作成功訊息",
  "data": {
    // 相關數據
  }
}
```

錯誤回應格式：

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "錯誤訊息",
  "details": {
    // 可選的詳細錯誤信息
  }
}
```

## 測試

### 執行測試

```bash
# 執行所有測試
python manage.py test edit_profile

# 執行特定測試類別
python manage.py test edit_profile.tests.ProfileUpdateTest

# 詳細輸出
python manage.py test edit_profile -v 2
```

### 測試範例

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from phone_auth.models import CustomUser

class ProfileUpdateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='pass123'
        )
    
    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/api/user/profile/',
            {'nickname': 'Test User'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## 配置要求

### settings.py

已添加以下配置：

```python
INSTALLED_APPS = [
    # ...
    'edit_profile',  # 新增
]

# 媒體檔案配置
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### urls.py

已添加以下路由：

```python
urlpatterns = [
    # ...
    path('api/user/', include('edit_profile.urls')),
]

# 開發環境媒體檔案服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 前端集成

### React 範例

```jsx
function ProfileForm() {
  const [profile, setProfile] = useState(null);
  
  useEffect(() => {
    // 獲取個人資料
    fetch('/api/user/profile/', {
      headers: {'Authorization': `Bearer ${token}`}
    })
    .then(r => r.json())
    .then(data => setProfile(data.data));
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/user/profile/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profile)
    });
    console.log(await res.json());
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        value={profile?.nickname}
        onChange={e => setProfile({...profile, nickname: e.target.value})}
      />
      <button type="submit">保存</button>
    </form>
  );
}
```

## 常見問題

### Q: 為什麼上傳頭像時收到 401 錯誤？

A: 確保在請求的 Authorization header 中包含有效的 token：
```
Authorization: Bearer YOUR_VALID_TOKEN
```

### Q: 上傳的圖片在哪裡？

A: 圖片儲存在 `media/avatars/YYYY/MM/DD/` 目錄中，可通過 `avatar_url` 字段訪問。

### Q: 支援哪些圖片格式？

A: 支援 Django ImageField 支援的所有格式：JPG、PNG、GIF、WebP 等（需安裝 Pillow）。

### Q: 如何在生產環境提供媒體檔案？

A: 使用 CDN（如 AWS S3）或配置 Nginx 反向代理。詳見 [設定指南](../../guides/EDIT_PROFILE_SETUP.md)。

## 性能考慮

1. **圖片優化**：使用 Pillow 自動壓縮大型圖片
2. **快取**：對媒體檔案啟用 HTTP 快取
3. **資料庫**：為常用欄位建立索引
4. **非同步**：考慮使用 Celery 進行大檔案處理

## 安全性

- ✅ 所有端點需要用戶認證
- ✅ 使用者只能編輯自己的資料
- ✅ 檔案大小限制（5MB）
- ✅ 完整的輸入驗證
- ✅ CORS 保護
- ✅ SQL 注入防護（使用 ORM）

## 相關文件

- [API 規格文件](../../guides/EDIT_PROFILE_API_SPEC.md) - 詳細的 API 文檔
- [測試指南](../../guides/EDIT_PROFILE_TESTING.md) - 測試方法和範例
- [設定指南](../../guides/EDIT_PROFILE_SETUP.md) - 安裝和配置步驟
- [快速參考](../../guides/EDIT_PROFILE_QUICK_REFERENCE.md) - 快速查詢表

## 貢獻

如有建議或 bug 報告，請聯絡開發團隊。

## 許可證

遵循主專案的許可證協議。

---

**最後更新**: 2024-11-18
**版本**: 1.0.0

