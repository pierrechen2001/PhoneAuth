# 個人資料編輯模組安裝和配置指南

## 目錄結構

```
PhoneOath/
├── edit_profile/                    # 新的個人資料編輯模組
│   ├── __init__.py
│   ├── apps.py                      # 應用程式配置
│   ├── admin.py                     # Django Admin 配置
│   ├── models.py                    # 資料模型
│   ├── views.py                     # API 視圖
│   ├── serializers.py               # 序列化器
│   ├── urls.py                      # URL 路由
│   └── tests.py                     # 單位測試
├── phone_auth/                      # 手機驗證模組（既有）
├── config/
│   ├── settings.py                  # 已更新：添加 edit_profile app 和媒體檔案設定
│   ├── urls.py                      # 已更新：添加 edit_profile 路由和媒體檔案服務
│   └── ...
├── guides/
│   ├── EDIT_PROFILE_API_SPEC.md     # API 規格文件
│   ├── EDIT_PROFILE_TESTING.md      # 測試指南
│   └── EDIT_PROFILE_SETUP.md        # 本文件
└── ...
```

## 安裝步驟

### 1. 創建必要的目錄

```bash
# 媒體檔案目錄（用於儲存上傳的頭像）
mkdir -p media/avatars
```

### 2. 更新依賴

如果需要支援圖片上傳，可能需要 Pillow 庫：

```bash
pip install Pillow

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 3. 執行資料庫遷移

```bash
# 建立遷移文件
python manage.py makemigrations

# 應用遷移
python manage.py migrate
```

預期輸出：
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, edit_profile, phone_auth, sessions
Running migrations:
  ...
  Applying phone_auth.0002_customuser_avatar_customuser_avatar_url_and_more... OK
```

### 4. 驗證安裝

```bash
# 進入 Django shell 驗證模型
python manage.py shell
>>> from phone_auth.models import CustomUser
>>> user = CustomUser.objects.first()
>>> print(user.nickname, user.avatar)
```

## 配置說明

### settings.py 更新

已添加以下配置：

```python
# 添加到 INSTALLED_APPS
'edit_profile',  # 個人資料編輯模組

# 媒體檔案設定
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### urls.py 更新

已添加以下路由：

```python
# 個人資料編輯 API
path('api/user/', include('edit_profile.urls')),

# 媒體檔案服務（開發環境）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### models.py 更新

已添加以下欄位到 `CustomUser` 模型：

```python
# 頭像相關欄位
avatar = models.ImageField(...)
avatar_url = models.CharField(...)
avatar_uploaded_at = models.DateTimeField(...)

# 個人資料欄位
nickname = models.CharField(...)
gender = models.CharField(...)
age = models.CharField(...)
degree = models.CharField(...)
counseling_record = models.IntegerField(...)
motivation_1, motivation_2, motivation_3 = models.CharField(...)
on_stage = models.CharField(...)
status = models.CharField(...)
retry_time = models.DateTimeField(...)
monkey_try = models.IntegerField(...)
```

## API 端點列表

| 方法 | 端點 | 功能 | 認證 |
|-----|------|------|------|
| GET | `/api/user/profile/` | 獲取個人資料 | 必須 |
| PATCH | `/api/user/profile/` | 更新個人資料 | 必須 |
| POST | `/api/user/avatar/upload/` | 上傳頭像 | 必須 |
| DELETE | `/api/user/avatar/` | 刪除頭像 | 必須 |

## 前端集成指南

### React 範例

```jsx
import React, { useState, useEffect } from 'react';

function ProfileEditor() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('/api/user/profile/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setProfile(data.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const updateProfile = async (updatedData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/user/profile/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });
      const data = await response.json();
      if (data.success) {
        setProfile(data.data);
        alert('個人資料更新成功！');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const uploadAvatar = async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    
    try {
      const response = await fetch('/api/user/avatar/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });
      const data = await response.json();
      if (data.success) {
        setProfile(prev => ({
          ...prev,
          avatar_url: data.data.avatar_url,
        }));
        alert('頭像上傳成功！');
      }
    } catch (error) {
      console.error('Error uploading avatar:', error);
    }
  };

  if (!profile) return <div>載入中...</div>;

  return (
    <div>
      <h1>編輯個人資料</h1>
      <input
        type="text"
        value={profile.nickname}
        onChange={(e) => setProfile({...profile, nickname: e.target.value})}
        placeholder="暱稱"
      />
      <input
        type="file"
        accept="image/*"
        onChange={(e) => uploadAvatar(e.target.files[0])}
      />
      <button 
        onClick={() => updateProfile({nickname: profile.nickname})}
        disabled={loading}
      >
        儲存
      </button>
    </div>
  );
}

export default ProfileEditor;
```

### Vue 3 範例

```vue
<template>
  <div class="profile-editor">
    <h1>編輯個人資料</h1>
    <form @submit.prevent="updateProfile">
      <input
        v-model="form.nickname"
        type="text"
        placeholder="暱稱"
      />
      <input
        v-model="form.gender"
        type="text"
        placeholder="性別"
      />
      <input
        type="file"
        @change="handleAvatarUpload"
        accept="image/*"
      />
      <button type="submit" :disabled="loading">儲存</button>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';

const form = reactive({
  nickname: '',
  gender: '',
});
const loading = ref(false);

const updateProfile = async () => {
  loading.value = true;
  try {
    const response = await fetch('/api/user/profile/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form),
    });
    const data = await response.json();
    if (data.success) {
      alert('個人資料更新成功！');
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
};

const handleAvatarUpload = async (event) => {
  const file = event.target.files[0];
  const formData = new FormData();
  formData.append('avatar', file);
  
  try {
    const response = await fetch('/api/user/avatar/upload/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    });
    const data = await response.json();
    if (data.success) {
      alert('頭像上傳成功！');
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
</script>
```

## 生產環境配置

### 1. 更新 settings.py

```python
# 生產環境設定
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# 使用 AWS S3 或其他雲端存儲服務
# 安裝 django-storages: pip install django-storages boto3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
```

### 2. 配置 Nginx

```nginx
location /media/ {
    alias /path/to/PhoneOath/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 3. 收集靜態檔案

```bash
python manage.py collectstatic
```

## 常見問題

### Q1: ImageField 報錯「模組 PIL 無法找到」

**A1:** 安裝 Pillow 庫

```bash
pip install Pillow
```

### Q2: 上傳的檔案無法存取

**A2:** 確保媒體目錄存在且有正確的權限

```bash
mkdir -p media/avatars
chmod 755 media
```

### Q3: 如何限制上傳的圖片尺寸？

**A3:** 在 views.py 的 `upload_avatar` 函數中已實現 5MB 限制。可根據需要調整：

```python
# views.py 中的限制檢查
if avatar_file.size > 5 * 1024 * 1024:  # 修改這裡的大小限制
    return Response({...})
```

### Q4: 如何在生產環境使用 HTTPS 提供媒體檔案？

**A4:** 使用 CDN 或反向代理：

```nginx
# Nginx 配置
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    location /media/ {
        proxy_pass http://backend/media/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 性能優化建議

1. **圖片壓縮**
   - 使用 Pillow 的 ImageOps 自動壓縮
   - 考慮使用 WebP 格式

2. **快取配置**
   - 在媒體文件上設置 HTTP 快取
   - 使用 CDN 加速

3. **資料庫優化**
   - 建立索引：`avatar_uploaded_at`, `phone_verified`
   - 使用資料庫連接池

4. **非同步處理**
   - 使用 Celery 進行大文件上傳
   - 非同步圖片壓縮和縮圖生成

## 相關資源

- [Django 文件上傳](https://docs.djangoproject.com/en/4.2/topics/files/)
- [Django REST Framework 文件上傳](https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser)
- [Pillow 圖片處理](https://pillow.readthedocs.io/)
- [AWS S3 整合](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)

## 下一步

1. 執行資料庫遷移
2. 測試 API 端點
3. 集成到前端應用
4. 部署到生產環境

詳見：
- [API 規格](./EDIT_PROFILE_API_SPEC.md)
- [測試指南](./EDIT_PROFILE_TESTING.md)

