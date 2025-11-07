"""
API Serializers

定義所有 API 端點的輸入輸出格式。
包含詳細的欄位說明與驗證規則，方便前端團隊理解使用。
"""

from rest_framework import serializers
from django.core.validators import RegexValidator


class SendOTPSerializer(serializers.Serializer):
    """
    發送 OTP 驗證碼的請求格式
    
    API Endpoint: POST /auth/phone/send-otp/
    
    使用範例：
    {
        "country_code": "+886",
        "phone_number": "987654321"
    }
    """
    
    country_code = serializers.CharField(
        max_length=5,
        required=True,
        help_text='國碼，必須以 + 開頭（例如：+886 代表台灣）',
        validators=[
            RegexValidator(
                regex=r'^\+\d{1,3}$',
                message='國碼格式錯誤，應為 +1 到 +999'
            )
        ]
    )
    
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        help_text='手機號碼（不含國碼，例如：987654321）',
        validators=[
            RegexValidator(
                regex=r'^\d{7,15}$',
                message='手機號碼格式錯誤，應為 7-15 位數字'
            )
        ]
    )
    
    def validate(self, data):
        """
        組合完整的手機號碼
        """
        full_phone = f"{data['country_code']}{data['phone_number']}"
        data['full_phone_number'] = full_phone
        return data


class SendOTPResponseSerializer(serializers.Serializer):
    """
    發送 OTP 的回應格式
    
    成功回應範例：
    {
        "status": "OTP_SENT",
        "verification_id": "xxxxxxx",
        "message": "驗證碼已發送到您的手機",
        "expires_in": 300
    }
    """
    
    status = serializers.CharField(
        help_text='狀態碼：OTP_SENT（已發送）、TOO_MANY_REQUESTS（請求過於頻繁）'
    )
    
    verification_id = serializers.CharField(
        required=False,
        help_text='Firebase 返回的驗證 session ID，前端需保存此 ID 用於驗證'
    )
    
    message = serializers.CharField(
        help_text='給使用者的訊息'
    )
    
    expires_in = serializers.IntegerField(
        required=False,
        help_text='驗證碼有效期限（秒），通常為 300 秒（5 分鐘）'
    )


class VerifyOTPSerializer(serializers.Serializer):
    """
    驗證 OTP 的請求格式
    
    API Endpoint: POST /auth/phone/verify-otp/
    
    使用 verification_id + otp_code（固定 6 位 OTP）
    {
        "verification_id": "xxxxxx",
        "otp_code": "123456"
    }
    
    """
    
    verification_id = serializers.CharField(
        required=True,
        help_text='Firebase verification session ID（方法一使用）'
    )
    
    otp_code = serializers.CharField(
        max_length=6,
        required=True,
        help_text='使用者輸入的驗證碼（6 位數字）',
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message='驗證碼格式錯誤，應為 6 位數字'
            )
        ]
    )
    


class VerifyOTPResponseSerializer(serializers.Serializer):
    """
    驗證 OTP 的回應格式
    
    成功回應範例：
    {
        "status": "VERIFIED",
        "phone_number": "+886987654321",
        "message": "手機號碼驗證成功"
    }
    
    失敗回應範例：
    {
        "status": "INVALID_OTP",
        "remaining_attempts": 2,
        "message": "驗證碼錯誤，您還有 2 次機會"
    }
    
    鎖定回應範例：
    {
        "status": "LOCKED",
        "message": "驗證失敗次數過多，請重新發送驗證碼"
    }
    """
    
    status = serializers.CharField(
        help_text='狀態：VERIFIED（成功）、INVALID_OTP（錯誤）、LOCKED（已鎖定）'
    )
    
    phone_number = serializers.CharField(
        required=False,
        help_text='已驗證的手機號碼（僅在成功時返回）'
    )
    
    message = serializers.CharField(
        help_text='給使用者的訊息'
    )
    
    remaining_attempts = serializers.IntegerField(
        required=False,
        help_text='剩餘嘗試次數（僅在驗證失敗時返回）'
    )


class ResendOTPSerializer(serializers.Serializer):
    """
    重新發送 OTP 的請求格式
    
    API Endpoint: POST /auth/phone/resend-otp/
    
    使用範例：
    {
        "phone_number": "+886987654321"
    }
    
    注意：前端應實作 60 秒的 rate limiting
    """
    
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        help_text='完整手機號碼（包含國碼，例如：+886987654321）',
        validators=[
            RegexValidator(
                regex=r'^\+\d{1,3}\d{7,15}$',
                message='手機號碼格式錯誤，應為：+國碼手機號碼'
            )
        ]
    )


class ResendOTPResponseSerializer(serializers.Serializer):
    """
    重新發送 OTP 的回應格式
    
    成功回應範例：
    {
        "status": "OTP_RESENT",
        "verification_id": "new_xxxxxx",
        "message": "驗證碼已重新發送",
        "retry_after": 60
    }
    
    頻率限制回應範例：
    {
        "status": "TOO_MANY_REQUESTS",
        "message": "請稍後再試",
        "retry_after": 45
    }
    """
    
    status = serializers.CharField(
        help_text='狀態：OTP_RESENT（已重新發送）、TOO_MANY_REQUESTS（請求過於頻繁）'
    )
    
    verification_id = serializers.CharField(
        required=False,
        help_text='新的 verification session ID'
    )
    
    message = serializers.CharField(
        help_text='給使用者的訊息'
    )
    
    retry_after = serializers.IntegerField(
        required=False,
        help_text='需要等待的秒數（通常為 60 秒）'
    )


class ErrorResponseSerializer(serializers.Serializer):
    """
    錯誤回應的統一格式
    
    範例：
    {
        "error": "AUTHENTICATION_REQUIRED",
        "message": "請先登入",
        "details": {
            "field": "auth_token",
            "issue": "Token 無效或已過期"
        }
    }
    """
    
    error = serializers.CharField(
        help_text='錯誤代碼'
    )
    
    message = serializers.CharField(
        help_text='錯誤訊息'
    )
    
    details = serializers.DictField(
        required=False,
        help_text='詳細錯誤資訊（可選）'
    )

