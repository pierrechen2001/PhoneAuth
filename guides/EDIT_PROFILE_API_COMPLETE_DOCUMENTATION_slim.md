## 個人資料檢視與編輯 API（edit_profile）


## 1. 模組功能

- **目的**：讓登入中的使用者可以：
  - 讀取自己的個人資料（Profile）
  - 更新個人資料欄位（暱稱、性別、年齡、學歷、動機…）
  - 上傳 / 刪除頭像
- **關聯**：`UserProfile` 一對一連到 `CustomUser`

### 資料模型

```python
class UserProfile(models.Model):
    id = UUIDField(primary_key=True)
    user = OneToOneField(CustomUser)  # 使用者

    nickname = CharField(max_length=150)
    gender = CharField(max_length=1)
    age = CharField(max_length=10)
    degree = CharField(max_length=20)
    motivation_1/2/3 = CharField(max_length=100, null=True)

    # 我新增了頭像相關
    avatar = ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, null=True)
    avatar_url = CharField(max_length=255, blank=True, null=True)
    avatar_uploaded_at = DateTimeField(blank=True, null=True)
```

### 認證方式

所有 API 都必須是「登入狀態」才可使用（`IsAuthenticated`）。  
目前預設開啟：

- **Session Authentication**：瀏覽器 / 同網域前端使用，靠 Cookie 帶 session
- **Basic Authentication**：方便用 Postman / curl 測試

> Token / JWT 沒有在專案中預設開啟，如要用可以再擴充。

---

## 2. API 一覽表

| 方法 | 路徑                         | 功能說明           |
|------|------------------------------|--------------------|
| GET  | `/api/user/profile/`        | 取得自己的個人資料 |
| PATCH| `/api/user/profile/`        | 更新個人資料       |
| POST | `/api/user/avatar/upload/`  | 上傳頭像           |
| DELETE | `/api/user/avatar/`       | 刪除頭像           |

---

## 3. 認證要怎麼帶？

### 3.1 前端（瀏覽器）建議用 Session

登入之後，後端會發 session cookie，之後請求只要加上：

```javascript
fetch('/api/user/profile/', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',          // 一定要加，才會帶 cookie
})
```

### 3.2 測試 / 腳本可用 Basic Auth

```bash
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Content-Type: application/json" \
  -u username:password
```

---

## 4. 詳細 API 說明

### 4.1 取得個人資料 `GET /api/user/profile/`

**用途**：拿到目前登入使用者的所有個人資料。如果還沒有 Profile，會自動建立一筆空的 Profile 再回傳。

**請求**

- 不需要 body
- 只要有登入（Session / Basic Auth）就可以

```http
GET /api/user/profile/
```

**成功回應範例**

```json
{
  "success": true,
  "message": "個人資料獲取成功",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "testuser",
    "email": "test@example.com",
    "nickname": "Test User",
    "gender": "M",
    "age": "25",
    "degree": "Bachelor",
    "motivation_1": "助人",
    "motivation_2": "成長",
    "motivation_3": "學習",
    "phone_number": "+886987654321",
    "phone_verified": true,
    "avatar_url": "http://localhost:8000/media/avatars/2025/11/28/av_test.png"
  }
}
```

**後端已實作邏輯**

- 每次呼叫都會用 `get_or_create(user=request.user)`，若沒有 Profile 會自動建立一筆
- 回傳格式固定為：`success + message + data`（`data` 是整理過的 Profile）
- 只會拿「自己的」資料，不會出現看到別人資料的情況

**目前實際測試與結果**

- 單元測試：
  - 已測試「正常取得資料」、「一開始沒有 Profile 時會自動建立」
  - 未登入時會被擋下（403），行為符合預期
- 手動測試：
  - 用瀏覽器 / Postman 帶登入狀態都能正常拿到資料

---

### 4.2 更新個人資料 `PATCH /api/user/profile/`

**用途**：更新自己的個人資料。  
**重點**：所有欄位都是「選填」，只傳你要改的欄位即可（部分更新）。

**可更新欄位**

| 欄位           | 類型   | 限制          | 說明      |
|----------------|--------|---------------|-----------|
| `nickname`     | string | ≤ 150 字元    | 暱稱      |
| `gender`       | string | 長度 1        | 性別 M/F  |
| `age`          | string | ≤ 10 字元     | 年齡      |
| `degree`       | string | ≤ 20 字元     | 學歷      |
| `motivation_1` | string | ≤ 100 字元    | 動機 1    |
| `motivation_2` | string | ≤ 100 字元    | 動機 2    |
| `motivation_3` | string | ≤ 100 字元    | 動機 3    |

**請求範例**

```http
PATCH /api/user/profile/
Content-Type: application/json
```

```json
{
  "nickname": "新的暱稱",
  "gender": "F"
}
```

**成功回應（重點）**

- 會回傳「更新後」的完整個人資料（同 GET）
- `success = true`、`message = "個人資料更新成功"`

**可能錯誤**

- 400：欄位長度超過限制等驗證錯誤，`error = "VALIDATION_ERROR"`
- 403：未登入 / 認證失敗

**後端已實作邏輯**

- 使用 `UpdateProfileSerializer` 做欄位驗證與長度檢查
- 只會更新你送出的欄位（部分更新），沒送的欄位不會被清空
- 對於 `None` 這類「明確要清空成 null」的情境，目前後端是 **不接受 null 寫進 CharField** 的（會回 400）

**目前實際測試與結果**

- 單元測試：
  - 已測試：成功更新、未登入被擋、所有欄位長度上限、空物件、空字串、只改單一欄位等情境
  - 有一個測試是「把 nickname 設成 null」，但因為模型不允許 null，實際回 400 —— 功能本身 OK，但是是否要這樣設計我也不太確定
- 手動測試：
  - 用前端表單 / curl 測過一般更新流程，資料都有正確寫入 DB

---

### 4.3 上傳頭像 `POST /api/user/avatar/upload/`

**用途**：上傳使用者頭像圖片。

**目前實際儲存方式（重要）**

- 檔案是直接存成「檔案」在伺服器本機磁碟，**不是存在資料庫、也不是雲端儲存**。
- 路徑格式：

```text
專案根目錄/
└── media/
    └── avatars/
        └── YYYY/
            └── MM/
                └── DD/
                    └── 檔案名稱.png
```

例如在你的機器上會長這樣：

- `/Users/guanyuchen/PhoneOath/media/avatars/2025/11/28/av_test.png`

資料庫只記：

- `avatar`：檔案路徑（相對於 `media`）
- `avatar_url`：完整 URL（給前端直接用）
- `avatar_uploaded_at`：上傳時間

**請求格式**

- Method：`POST`
- Content-Type：`multipart/form-data`
- 欄位：

| 欄位     | 類型 | 必填 | 說明                  |
|----------|------|------|-----------------------|
| `avatar` | file | ✅   | 圖片檔（JPG/PNG…）    |

**限制**

- 檔案大小：最多 5MB
- 非圖片 / 壞掉的檔案會被拒絕

**curl 範例**

```bash
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -b cookies.txt \
  -F "avatar=@/path/to/image.png"
```

**成功回應**

```json
{
  "success": true,
  "message": "頭像上傳成功",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "avatar_url": "http://localhost:8000/media/avatars/2025/11/28/av_test.png",
    "avatar_uploaded_at": "2025-11-28T14:30:00Z"
  }
}
```

**後端已實作邏輯**

- 用 `AvatarUploadSerializer` 驗證上傳欄位，確保真的有檔案
- 交給 Django 的 `ImageField` 做「是否為圖片」的檢查，再額外檢查檔案大小（> 5MB 直接擋掉）
- 實際圖片檔案存在本機 `media/avatars/...`，DB 只記路徑與對應的 `avatar_url`、`avatar_uploaded_at`

**目前實際測試與結果**

- 單元測試：
  - 已測試：成功上傳、未登入上傳、上傳純文字檔會被擋、刪除後再上傳等情境
  - 測「超過 5MB」那支測試，目前因為測試檔案本身不是合法圖片，會先被判定為 `invalid_image`，所以回傳 `VALIDATION_ERROR` 而不是 `FILE_TOO_LARGE`（屬於測試寫法問題，功能邏輯本身 OK）
- 手動測試：
  - 用小圖、不同格式（PNG/JPG）上傳過，頁面可正確顯示回傳的 `avatar_url`

---

### 4.4 刪除頭像 `DELETE /api/user/avatar/`

**用途**：把目前的頭像刪掉。

**行為說明**

- 會真的把頭像檔案從伺服器的 `media/avatars/...` 刪除
- 同時把 DB 裡的：
  - `avatar` 清空
  - `avatar_url` 清空
  - `avatar_uploaded_at` 設為 `null`
- **冪等**：就算本來就沒有頭像，呼叫也會回傳成功

**請求**

```http
DELETE /api/user/avatar/
```

**成功回應**

```json
{
  "success": true,
  "message": "頭像刪除成功"
}
```

---

## 5. 錯誤格式（統一）

所有自訂錯誤大致長這樣：

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "錯誤訊息",
  "details": { ...可選的欄位錯誤... }
}
```

常見 `error`：

| 錯誤代碼          | 代表意思                 |
|-------------------|--------------------------|
| `VALIDATION_ERROR`| 請求欄位驗證失敗         |
| `FILE_TOO_LARGE`  | 上傳檔案超過 5MB         |
| `GET_FAILED`      | 取個人資料時發生例外     |
| `UPDATE_FAILED`   | 更新個人資料時發生例外   |
| `UPLOAD_FAILED`   | 上傳頭像時發生例外       |
| `DELETE_FAILED`   | 刪除頭像時發生例外       |

HTTP 狀態碼：

- 200：成功
- 400：欄位錯誤 / 檔案不合法
- 401 / 403：沒有登入或沒有權限
- 500：伺服器端非預期錯誤

---

## 6. 快速使用範例

### 6.1 瀏覽器（Session）

```javascript
// 取得個人資料
const getProfile = async () => {
  const res = await fetch('/api/user/profile/', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  const json = await res.json();
  console.log(json.data);
};

// 更新個人資料
const updateProfile = async () => {
  const res = await fetch('/api/user/profile/', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ nickname: '新暱稱' }),
  });
  const json = await res.json();
  console.log(json.data);
};

// 上傳頭像
const uploadAvatar = async (file) => {
  const formData = new FormData();
  formData.append('avatar', file);

  const res = await fetch('/api/user/avatar/upload/', {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });
  const json = await res.json();
  console.log(json.data.avatar_url);
};
```

### 6.2 curl（Basic Auth）

```bash
# 取得個人資料
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Content-Type: application/json" \
  -u username:password

# 更新暱稱
curl -X PATCH http://localhost:8000/api/user/profile/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{"nickname": "New Name"}'

# 上傳頭像
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -u username:password \
  -F "avatar=@/path/to/image.png"
```


