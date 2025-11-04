手機號碼綁定驗證流程
使用者註冊帳號後，可以進入「綁定手機號碼」頁面進行驗證。
流程如下：
1. 使用者輸入「國碼 + 手機號碼」
2. 按下「發送簡訊驗證碼」 → 由 Firebase 送出 OTP
3. 進入「輸入驗證碼頁面」
4. 使用者輸入 4~6 位驗證碼（可錯 3 次）
5. 驗證成功後 → Django 後端更新使用者資料（phone_number_verified=True）

頁面與對應 API 規格
Page 1：綁定手機號碼頁面
API: POST /auth/phone/send-otp/  ( 輸入國碼 + 手機號碼 → 按「發送驗證碼」)
Request Body:
{ "country_code": "+886",
  "phone_number": "987654321"}
後端行為：
檢查是否登入（綁定功能需登入）


組合完整號碼：+886987654321


呼叫 Firebase Phone Auth API 發送驗證碼 （轉給 Firebase SDK）


回傳 verificationId（Firebase 生成的驗證 session id）


Response:
{ "status": "OTP_SENT",
  "verification_id": "xxxxxxx"}

Page 2：輸入驗證碼頁面
API: POST /auth/phone/verify-otp/  （使用者輸入 OTP → 點「驗證」）
Request Body:
{ "verification_id": "xxxxxx",
  "otp_code": "123456"}
後端行為：
呼叫 Firebase Auth 驗證該 OTP（使用 Admin SDK）
credential = auth.PhoneAuthProvider.credential(verification_id, otp_code)
user_record = auth.verify_id_token(credential)
記錄驗證狀態、錯誤次數
回傳成功 / 失敗狀態
驗證成功 → 更新本地使用者資料表
user.phone_number = verified_phone
user.phone_verified = True
user.save()
Response:
{ "status": "VERIFIED",
  "phone_number": "+886963779263"}
錯誤次數限制
每個驗證 session 最多輸入錯誤 3 次
達上限 → status: "LOCKED"
再次綁定需重新送出 OTP



Page 3：重新發送驗證碼
API: POST /auth/phone/resend-otp/  （每 60 秒可按一次「重新發送」）
Request Body:
{ "phone_number": "+886963779263"}
邏輯：
前端檢查前次請求時間（Rate Limit：60 秒）
呼叫 Firebase 重新發送 OTP
更新 verification_id
Response:
{ "status": "OTP_RESENT",
  "verification_id": "new_xxxxxx"}


Firebase Auth 端需做的設定

資料表欄位
在 Firebase Auth 裡：
uid（Firebase user ID）
phoneNumber（手機號碼）
phoneVerified（系統自帶欄位）
在 SQL 裡需要新增：
phone_number, char[20] （含國碼完整手機號碼）
phone_verified, boolean （是否驗證通過）
otp_attempts, int （嘗試次數）
status, text （當前驗證狀態）[“OTP_SENT”, “OTP_RESENT”, “VERIFIED”, “INVALID_OTP”, “LOCKED”, “TOO_MANY_REQUESTS”]
