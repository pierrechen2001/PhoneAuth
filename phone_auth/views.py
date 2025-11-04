"""
API Views

實現所有手機驗證相關的 API 端點。
包含詳細的錯誤處理與日誌記錄。
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import logging

from .serializers import (
    SendOTPSerializer,
    SendOTPResponseSerializer,
    VerifyOTPSerializer,
    VerifyOTPResponseSerializer,
    ResendOTPSerializer,
    ResendOTPResponseSerializer,
    ErrorResponseSerializer
)
from .firebase_service import firebase_service
from .models import CustomUser, OTPVerificationLog

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_otp(request):
    """
    發送 OTP 驗證碼
    
    API Endpoint: POST /auth/phone/send-otp/
    
    Request Body:
    {
        "country_code": "+886",
        "phone_number": "987654321"
    }
    
    Response (Success):
    {
        "status": "OTP_SENT",
        "verification_id": "xxxxxxx",
        "message": "驗證碼已發送到您的手機",
        "expires_in": 300
    }
    
    Response (Error):
    {
        "error": "TOO_MANY_REQUESTS",
        "message": "請求過於頻繁，請稍後再試",
        "retry_after": 45
    }
    
    注意事項：
    1. 需要登入才能綁定手機號碼
    2. 實際的 OTP 發送在前端使用 Firebase JS SDK 完成
    3. 前端應將 Firebase 返回的 verification_id 儲存，用於後續驗證
    """
    
    # 驗證輸入資料
    serializer = SendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'error': 'VALIDATION_ERROR',
                'message': '輸入資料格式錯誤',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    full_phone_number = validated_data['full_phone_number']
    user = request.user
    
    # 檢查 Rate Limiting（60 秒內不可重複發送）
    if user.last_otp_sent_at:
        time_since_last = timezone.now() - user.last_otp_sent_at
        if time_since_last < timedelta(seconds=60):
            remaining = 60 - int(time_since_last.total_seconds())
            logger.warning(f"使用者 {user.username} 請求過於頻繁")
            return Response(
                {
                    'status': 'TOO_MANY_REQUESTS',
                    'message': f'請求過於頻繁，請等待 {remaining} 秒後再試',
                    'retry_after': remaining
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
    
    # 檢查手機號碼是否已被其他使用者綁定
    existing_user = CustomUser.objects.filter(
        phone_number=full_phone_number,
        phone_verified=True
    ).exclude(id=user.id).first()
    
    if existing_user:
        logger.warning(f"手機號碼 {full_phone_number} 已被其他使用者綁定")
        return Response(
            {
                'error': 'PHONE_ALREADY_BOUND',
                'message': '此手機號碼已被其他帳號綁定'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 呼叫 Firebase 服務發送 OTP
    # 注意：實際發送在前端完成，這裡主要是記錄狀態
    result = firebase_service.send_otp(full_phone_number)
    
    if result.get('success'):
        # 更新使用者狀態
        user.phone_number = full_phone_number
        user.verification_status = CustomUser.VerificationStatus.OTP_SENT
        user.last_otp_sent_at = timezone.now()
        user.otp_attempts = 0  # 重置嘗試次數
        user.save()
        
        # 記錄日誌
        OTPVerificationLog.objects.create(
            user=user,
            phone_number=full_phone_number,
            action='SEND',
            success=True
        )
        
        logger.info(f"OTP 發送請求成功：user={user.username}, phone={full_phone_number}")
        
        return Response(
            {
                'status': 'OTP_SENT',
                'message': '驗證碼已發送到您的手機，請在前端完成 Firebase Phone Auth 流程',
                'expires_in': 300,
                'note': '前端需使用 Firebase JS SDK 的 signInWithPhoneNumber 方法，並將返回的 verificationId 傳給 verify-otp API'
            },
            status=status.HTTP_200_OK
        )
    else:
        # 發送失敗
        error_msg = result.get('error', '未知錯誤')
        logger.error(f"OTP 發送失敗：user={user.username}, error={error_msg}")
        
        # 記錄日誌
        OTPVerificationLog.objects.create(
            user=user,
            phone_number=full_phone_number,
            action='SEND',
            success=False,
            error_message=error_msg
        )
        
        return Response(
            {
                'error': 'SEND_OTP_FAILED',
                'message': f'發送驗證碼失敗：{error_msg}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    """
    驗證 OTP 代碼
    
    API Endpoint: POST /auth/phone/verify-otp/
    
    Request Body (方法一 - 傳統方式):
    {
        "verification_id": "xxxxxx",
        "otp_code": "123456"
    }
    
    Request Body (方法二 - 建議使用):
    {
        "id_token": "eyJhbGciOiJSUzI1NiIs..."
    }
    
    Response (Success):
    {
        "status": "VERIFIED",
        "phone_number": "+886987654321",
        "message": "手機號碼驗證成功"
    }
    
    Response (Failed):
    {
        "status": "INVALID_OTP",
        "remaining_attempts": 2,
        "message": "驗證碼錯誤，您還有 2 次機會"
    }
    
    Response (Locked):
    {
        "status": "LOCKED",
        "message": "驗證失敗次數過多，請重新發送驗證碼"
    }
    
    注意事項：
    1. 建議使用方法二（id_token），安全性更高
    2. 每個 verification session 最多錯誤 3 次
    3. 達到錯誤上限後需重新發送 OTP
    """
    
    # 驗證輸入資料
    serializer = VerifyOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'error': 'VALIDATION_ERROR',
                'message': '輸入資料格式錯誤',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    user = request.user
    
    # 檢查是否已鎖定
    if user.verification_status == CustomUser.VerificationStatus.LOCKED:
        logger.warning(f"使用者 {user.username} 已被鎖定")
        return Response(
            {
                'status': 'LOCKED',
                'message': '驗證失敗次數過多，請重新發送驗證碼'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # 方法二：使用 ID Token（建議）
    if 'id_token' in validated_data:
        id_token = validated_data['id_token']
        result = firebase_service.verify_id_token(id_token)
        
        if result.get('success'):
            verified_phone = result.get('phone_number')
            firebase_uid = result.get('uid')
            
            # 更新使用者資料
            user.phone_number = verified_phone
            user.phone_verified = True
            user.verification_status = CustomUser.VerificationStatus.VERIFIED
            user.otp_attempts = 0
            user.save()
            
            # 記錄日誌
            OTPVerificationLog.objects.create(
                user=user,
                phone_number=verified_phone,
                action='VERIFY_SUCCESS',
                success=True
            )
            
            logger.info(f"手機驗證成功：user={user.username}, phone={verified_phone}")
            
            return Response(
                {
                    'status': 'VERIFIED',
                    'phone_number': verified_phone,
                    'message': '手機號碼驗證成功'
                },
                status=status.HTTP_200_OK
            )
        else:
            # 驗證失敗
            user.increment_otp_attempts()
            remaining = 3 - user.otp_attempts
            
            error_msg = result.get('error', '驗證失敗')
            logger.warning(f"手機驗證失敗：user={user.username}, attempts={user.otp_attempts}")
            
            # 記錄日誌
            OTPVerificationLog.objects.create(
                user=user,
                phone_number=user.phone_number or '',
                action='VERIFY_FAILED',
                success=False,
                error_message=error_msg
            )
            
            if user.verification_status == CustomUser.VerificationStatus.LOCKED:
                return Response(
                    {
                        'status': 'LOCKED',
                        'message': '驗證失敗次數過多，請重新發送驗證碼'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                return Response(
                    {
                        'status': 'INVALID_OTP',
                        'remaining_attempts': remaining,
                        'message': f'驗證碼錯誤，您還有 {remaining} 次機會'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
    
    # 方法一：使用 verification_id + otp_code（傳統方式）
    else:
        verification_id = validated_data['verification_id']
        otp_code = validated_data['otp_code']
        
        result = firebase_service.verify_otp(verification_id, otp_code)
        
        # 處理邏輯同上（為簡化，此處省略重複代碼）
        # 實際專案中應將驗證邏輯抽取為共用方法
        
        if result.get('success'):
            # 模擬驗證成功（實際應從 result 取得已驗證的手機號碼）
            verified_phone = user.phone_number
            
            user.phone_verified = True
            user.verification_status = CustomUser.VerificationStatus.VERIFIED
            user.otp_attempts = 0
            user.save()
            
            logger.info(f"手機驗證成功：user={user.username}, phone={verified_phone}")
            
            return Response(
                {
                    'status': 'VERIFIED',
                    'phone_number': verified_phone,
                    'message': '手機號碼驗證成功'
                },
                status=status.HTTP_200_OK
            )
        else:
            user.increment_otp_attempts()
            remaining = 3 - user.otp_attempts
            
            if user.verification_status == CustomUser.VerificationStatus.LOCKED:
                return Response(
                    {
                        'status': 'LOCKED',
                        'message': '驗證失敗次數過多，請重新發送驗證碼'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                return Response(
                    {
                        'status': 'INVALID_OTP',
                        'remaining_attempts': remaining,
                        'message': f'驗證碼錯誤，您還有 {remaining} 次機會'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_otp(request):
    """
    重新發送 OTP 驗證碼
    
    API Endpoint: POST /auth/phone/resend-otp/
    
    Request Body:
    {
        "phone_number": "+886987654321"
    }
    
    Response (Success):
    {
        "status": "OTP_RESENT",
        "verification_id": "new_xxxxxx",
        "message": "驗證碼已重新發送",
        "retry_after": 60
    }
    
    Response (Rate Limited):
    {
        "status": "TOO_MANY_REQUESTS",
        "message": "請稍後再試",
        "retry_after": 45
    }
    
    注意事項：
    1. Rate Limiting：60 秒內只能發送一次
    2. 重新發送後會重置錯誤次數
    3. 會產生新的 verification_id
    """
    
    # 驗證輸入資料
    serializer = ResendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'error': 'VALIDATION_ERROR',
                'message': '輸入資料格式錯誤',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    phone_number = validated_data['phone_number']
    user = request.user
    
    # 驗證手機號碼是否屬於當前使用者
    if user.phone_number != phone_number:
        logger.warning(f"使用者 {user.username} 嘗試重發不屬於自己的手機號碼 OTP")
        return Response(
            {
                'error': 'PHONE_MISMATCH',
                'message': '手機號碼不符'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 檢查 Rate Limiting（60 秒內不可重複發送）
    if user.last_otp_sent_at:
        time_since_last = timezone.now() - user.last_otp_sent_at
        if time_since_last < timedelta(seconds=60):
            remaining = 60 - int(time_since_last.total_seconds())
            logger.warning(f"使用者 {user.username} 重發請求過於頻繁")
            return Response(
                {
                    'status': 'TOO_MANY_REQUESTS',
                    'message': f'請求過於頻繁，請等待 {remaining} 秒後再試',
                    'retry_after': remaining
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
    
    # 呼叫 Firebase 服務重新發送 OTP
    result = firebase_service.send_otp(phone_number)
    
    if result.get('success'):
        # 更新使用者狀態
        user.verification_status = CustomUser.VerificationStatus.OTP_RESENT
        user.last_otp_sent_at = timezone.now()
        user.otp_attempts = 0  # 重置嘗試次數
        user.save()
        
        # 記錄日誌
        OTPVerificationLog.objects.create(
            user=user,
            phone_number=phone_number,
            action='RESEND',
            success=True
        )
        
        logger.info(f"OTP 重發成功：user={user.username}, phone={phone_number}")
        
        return Response(
            {
                'status': 'OTP_RESENT',
                'message': '驗證碼已重新發送',
                'retry_after': 60,
                'note': '前端需使用 Firebase JS SDK 重新發送，並將新的 verificationId 傳給 verify-otp API'
            },
            status=status.HTTP_200_OK
        )
    else:
        # 發送失敗
        error_msg = result.get('error', '未知錯誤')
        logger.error(f"OTP 重發失敗：user={user.username}, error={error_msg}")
        
        # 記錄日誌
        OTPVerificationLog.objects.create(
            user=user,
            phone_number=phone_number,
            action='RESEND',
            success=False,
            error_message=error_msg
        )
        
        return Response(
            {
                'error': 'RESEND_OTP_FAILED',
                'message': f'重新發送驗證碼失敗：{error_msg}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

