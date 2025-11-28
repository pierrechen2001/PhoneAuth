"""
個人資料編輯 API Views

實現個人資料編輯和頭像上傳相關的 API 端點。
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import logging

from .models import UserProfile
from phone_auth.models import CustomUser

logger = logging.getLogger(__name__)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    更新使用者個人資料
    
    API Endpoint: PATCH /api/user/profile/
    
    Request Body:
    {
        "nickname": "Pierre",
        "gender": "M",
        "age": "23",
        "degree": "Bachelor",
        "motivation_1": "助人",
        "motivation_2": "成長",
        "motivation_3": "學習"
    }
    
    Response (Success):
    {
        "success": true,
        "message": "個人資料更新成功",
        "data": {
            "id": "uuid",
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
            "phone_verified": true,
            "avatar_url": null
        }
    }
    """
    
    # 驗證輸入資料
    serializer = UpdateProfileSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"使用者 {request.user.username} 個人資料驗證失敗：{serializer.errors}")
        return Response(
            {
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '驗證錯誤',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    user = request.user
    
    try:
        # 獲取或建立 UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # 更新欄位
        for field, value in validated_data.items():
            if value is not None:
                setattr(profile, field, value)
        
        profile.save()
        
        # 使用 Serializer 構建回應
        response_serializer = ProfileResponseSerializer(profile)
        
        logger.info(f"使用者 {user.username} 個人資料更新成功")
        
        return Response(
            {
                'success': True,
                'message': '個人資料更新成功',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"更新使用者 {user.username} 個人資料時發生錯誤：{str(e)}")
        return Response(
            {
                'success': False,
                'error': 'UPDATE_FAILED',
                'message': '更新個人資料失敗'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    獲取使用者個人資料
    
    API Endpoint: GET /api/user/profile/
    """
    
    try:
        user = request.user
        
        # 獲取或建立 UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        response_serializer = ProfileResponseSerializer(profile)
        
        logger.info(f"使用者 {user.username} 獲取個人資料成功")
        
        return Response(
            {
                'success': True,
                'message': '個人資料獲取成功',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"獲取使用者 {request.user.username} 個人資料時發生錯誤：{str(e)}")
        return Response(
            {
                'success': False,
                'error': 'GET_FAILED',
                'message': '獲取個人資料失敗'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """
    上傳使用者頭像
    
    API Endpoint: POST /api/user/avatar/upload/
    """
    
    # 驗證輸入資料
    serializer = AvatarUploadSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"使用者 {request.user.username} 頭像驗證失敗：{serializer.errors}")
        return Response(
            {
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '驗證錯誤',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = request.user
        avatar_file = serializer.validated_data['avatar']
        
        # 檢查圖片尺寸（限制為 5MB）
        if avatar_file.size > 5 * 1024 * 1024:
            logger.warning(f"使用者 {user.username} 上傳圖片過大：{avatar_file.size} bytes")
            return Response(
                {
                    'success': False,
                    'error': 'FILE_TOO_LARGE',
                    'message': '圖片檔案過大，請上傳不超過 5MB 的圖片'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 獲取或建立 UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # 更新頭像
        profile.avatar = avatar_file
        profile.avatar_uploaded_at = timezone.now()
        profile.save()
        
        # 構建頭像 URL
        avatar_url = request.build_absolute_uri(profile.avatar.url) if profile.avatar else None
        profile.avatar_url = avatar_url  # 更新 DB 中的 avatar_url
        profile.save(update_fields=['avatar_url'])
        
        response_serializer = AvatarResponseSerializer(profile)
        
        logger.info(f"使用者 {user.username} 頭像上傳成功")
        
        return Response(
            {
                'success': True,
                'message': '頭像上傳成功',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"使用者 {request.user.username} 上傳頭像時發生錯誤：{str(e)}")
        return Response(
            {
                'success': False,
                'error': 'UPLOAD_FAILED',
                'message': '上傳頭像失敗'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """
    刪除使用者頭像
    
    API Endpoint: DELETE /api/user/avatar/
    """
    
    try:
        user = request.user
        
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'success': True,
                    'message': '頭像已刪除（無個人資料）'
                },
                status=status.HTTP_200_OK
            )
        
        # 刪除頭像檔案
        if profile.avatar:
            profile.avatar.delete()
        
        profile.avatar_uploaded_at = None
        profile.avatar_url = None
        profile.save()
        
        logger.info(f"使用者 {user.username} 頭像刪除成功")
        
        return Response(
            {
                'success': True,
                'message': '頭像刪除成功'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"使用者 {request.user.username} 刪除頭像時發生錯誤：{str(e)}")
        return Response(
            {
                'success': False,
                'error': 'DELETE_FAILED',
                'message': '刪除頭像失敗'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

