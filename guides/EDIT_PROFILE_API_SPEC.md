# 個人資料編輯 API 規格

## 概述

此文件定義了個人資料編輯相關的所有 API 端點。所有 API 都需要使用者登入。

---

## API 端點

### 1. 獲取個人資料

**Endpoint:** `GET /api/user/profile/`

**認證:** 必須登入 (IsAuthenticated)

**Description:** 獲取當前登入使用者的完整個人資料

**Request:**
```bash
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "個人資料獲取成功",
  "data": {
    "id": 1,
    "username": "pierre",
    "email": "pierre@example.com",
    "nickname": "Pierre",
    "gender": "M",
    "age": "23",
    "degree": "Bachelor",
    "motivation_1": "助人",
    "motivation_2": "成長",
    "motivation_3": "學習",
    "phone_number": "+886987654321",
    "phone_verified": true
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 2. 更新個人資料

**Endpoint:** `PATCH /api/user/profile/`

**認證:** 必須登入 (IsAuthenticated)

**Description:** 更新當前登入使用者的個人資料。所有欄位都是選擇性的，只提交要更新的欄位。

**Request Body:**
```json
{
  "nickname": "Pierre",
  "gender": "M",
  "age": "23",
  "degree": "Bachelor",
  "motivation_1": "助人",
  "motivation_2": "成長",
  "motivation_3": "學習"
}
```

**Supported Fields:**
- `nickname` (string, max 150): 使用者暱稱
- `gender` (string, max 1): 使用者性別
- `age` (string, max 10): 使用者年齡
- `degree` (string, max 20): 使用者學歷
- `motivation_1` (string, max 100, nullable): 動機1
- `motivation_2` (string, max 100, nullable): 動機2
- `motivation_3` (string, max 100, nullable): 動機3

**Request Example:**
```bash
curl -X PATCH http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Pierre",
    "gender": "M",
    "age": "23",
    "degree": "Bachelor"
  }'
```

**Response (200 OK):**
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
    "degree": "Bachelor",
    "motivation_1": null,
    "motivation_2": null,
    "motivation_3": null,
    "phone_number": "+886987654321",
    "phone_verified": true
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "驗證錯誤",
  "details": {
    "age": ["This field may not be blank."]
  }
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "UPDATE_FAILED",
  "message": "更新個人資料失敗"
}
```

---

### 3. 上傳頭像

**Endpoint:** `POST /api/user/avatar/upload/`

**認證:** 必須登入 (IsAuthenticated)

**Content-Type:** `multipart/form-data`

**Description:** 上傳使用者頭像。支援的圖片格式：JPG、PNG、GIF。最大檔案大小：5MB。

**Request Form Data:**
- `avatar` (file, required): 圖片檔案

**Request Example:**
```bash
curl -X POST http://localhost:8000/api/user/avatar/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "avatar=@/path/to/image.jpg"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "頭像上傳成功",
  "data": {
    "id": 1,
    "avatar_url": "http://localhost:8000/media/avatars/2024/11/18/image.jpg",
    "avatar_uploaded_at": "2024-11-18T10:30:45.123456Z"
  }
}
```

**Response (400 Bad Request - File Too Large):**
```json
{
  "success": false,
  "error": "FILE_TOO_LARGE",
  "message": "圖片檔案過大，請上傳不超過 5MB 的圖片"
}
```

**Response (400 Bad Request - Invalid Image):**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "驗證錯誤",
  "details": {
    "avatar": ["The submitted data was not a file. Check the encoding type on the form."]
  }
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "UPLOAD_FAILED",
  "message": "上傳頭像失敗"
}
```

---

### 4. 刪除頭像

**Endpoint:** `DELETE /api/user/avatar/`

**認證:** 必須登入 (IsAuthenticated)

**Description:** 刪除使用者的頭像檔案和相關信息。

**Request Example:**
```bash
curl -X DELETE http://localhost:8000/api/user/avatar/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "頭像刪除成功"
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "DELETE_FAILED",
  "message": "刪除頭像失敗"
}
```

---

## 錯誤代碼

| 錯誤代碼 | HTTP 狀態碼 | 描述 |
|---------|-----------|------|
| VALIDATION_ERROR | 400 | 輸入資料驗證失敗 |
| FILE_TOO_LARGE | 400 | 上傳檔案過大（> 5MB） |
| UPDATE_FAILED | 500 | 更新個人資料失敗 |
| GET_FAILED | 500 | 獲取個人資料失敗 |
| UPLOAD_FAILED | 500 | 上傳頭像失敗 |
| DELETE_FAILED | 500 | 刪除頭像失敗 |

---

## 個人資料欄位說明

| 欄位名稱 | 類型 | 最大長度 | 可為空 | 說明 |
|---------|------|---------|-------|------|
| nickname | CharField | 150 | Yes | 使用者暱稱 |
| gender | CharField | 1 | Yes | 使用者性別（M/F/O） |
| age | CharField | 10 | Yes | 使用者年齡 |
| degree | CharField | 20 | Yes | 使用者學歷 |
| motivation_1 | CharField | 100 | Yes | 第一個動機 |
| motivation_2 | CharField | 100 | Yes | 第二個動機 |
| motivation_3 | CharField | 100 | Yes | 第三個動機 |
| phone_number | CharField | 20 | Yes | 已驗證的手機號碼 |
| phone_verified | BooleanField | - | No | 手機是否已驗證 |

---

## 使用流程

### 前端流程

1. **頁面初始化**
   - 呼叫 `GET /api/user/profile/` 取得目前使用者資料
   - 在表單中填充使用者資料

2. **編輯個人資料**
   - 使用者在表單中修改資料
   - 點擊「儲存」按鈕

3. **提交更新**
   - 呼叫 `PATCH /api/user/profile/` 提交更新的欄位
   - 顯示成功/失敗訊息

4. **上傳頭像**
   - 使用者選擇圖片
   - 呼叫 `POST /api/user/avatar/upload/` 上傳
   - 顯示上傳結果

5. **刪除頭像**
   - 使用者點擊刪除按鈕
   - 呼叫 `DELETE /api/user/avatar/` 刪除
   - 更新頁面

---

## 安全性考慮

1. **認證**
   - 所有端點都需要使用者登入
   - 使用者只能編輯自己的資料

2. **檔案上傳**
   - 限制檔案大小為 5MB
   - 限制檔案類型為圖片
   - 檔案儲存在安全的目錄

3. **驗證**
   - 所有輸入都經過 Django Serializer 驗證
   - 欄位長度限制已在後端實施

---

## 測試範例

### 使用 Postman

1. **設定認證**
   - Auth Type: Bearer Token
   - Token: 從登入 API 取得的 JWT token

2. **測試獲取個人資料**
   - Method: GET
   - URL: `http://localhost:8000/api/user/profile/`

3. **測試更新個人資料**
   - Method: PATCH
   - URL: `http://localhost:8000/api/user/profile/`
   - Body (raw JSON):
   ```json
   {
     "nickname": "Test User",
     "age": "25"
   }
   ```

4. **測試上傳頭像**
   - Method: POST
   - URL: `http://localhost:8000/api/user/avatar/upload/`
   - Body: form-data
     - Key: avatar
     - Value: 選擇圖片檔案

---

## 數據庫遷移

在首次使用前，需要執行以下命令以建立必要的資料庫欄位：

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 相關資源

- [Phone Authentication API](./API_TESTING_GUIDE.md)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django File Upload](https://docs.djangoproject.com/en/4.2/topics/files/)

