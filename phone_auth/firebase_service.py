"""
Firebase Authentication 整合服務

此模組處理與 Firebase Phone Authentication 的所有互動。
包含：發送 OTP、驗證 OTP、以及 Firebase Admin SDK 的初始化。

使用前請確保：
1. 已在 Firebase Console 啟用 Phone Authentication
2. 已下載 Firebase service account JSON 檔案
3. 已在設定中配置 FIREBASE_CREDENTIALS_PATH
"""

import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FirebaseAuthService:
    """
    Firebase Authentication 服務類別
    
    封裝所有與 Firebase Phone Auth 相關的操作。
    使用單例模式確保 Firebase App 只初始化一次。
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """單例模式：確保只有一個實例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化 Firebase Admin SDK"""
        if not self._initialized:
            self._initialize_firebase()
            self.__class__._initialized = True
    
    def _initialize_firebase(self):
        """
        初始化 Firebase Admin SDK
        
        從設定檔讀取 credentials 並初始化 Firebase App。
        如果已經初始化過，則跳過。
        """
        try:
            # 檢查是否已經初始化
            firebase_admin.get_app()
            logger.info("Firebase App 已經初始化")
        except ValueError:
            # 尚未初始化，進行初始化
            try:
                cred_path = settings.FIREBASE_CREDENTIALS_PATH
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info(f"Firebase App 初始化成功，使用憑證：{cred_path}")
            except Exception as e:
                logger.error(f"Firebase 初始化失敗：{str(e)}")
                raise
    
    def send_otp(self, phone_number: str) -> dict:
        """
        發送 OTP 驗證碼到指定手機號碼
        
        注意：這是模擬實作。實際的 OTP 發送需要在前端使用 Firebase JS SDK。
        後端 Admin SDK 不直接支援發送 SMS，而是用於驗證。
        
        實際流程：
        1. 前端使用 Firebase JS SDK 的 RecaptchaVerifier 和 signInWithPhoneNumber
        2. Firebase 自動發送 SMS
        3. 前端收到 verificationId，傳給後端儲存
        
        Args:
            phone_number: 完整手機號碼（包含國碼，例如：+886987654321）
        
        Returns:
            dict: {
                'success': bool,
                'verification_id': str (如果成功),
                'error': str (如果失敗)
            }
        """
        try:
            # 驗證手機號碼格式
            if not phone_number.startswith('+'):
                return {
                    'success': False,
                    'error': '手機號碼必須包含國碼（以 + 開頭）'
                }
            
            # 注意：實際的 OTP 發送在前端完成
            # 這裡返回成功狀態，實際 verification_id 由前端提供
            logger.info(f"準備發送 OTP 到：{phone_number}")
            
            # 模擬返回（實際上由前端 Firebase SDK 處理）
            return {
                'success': True,
                'message': 'OTP 發送請求已接受，請在前端完成 Firebase Phone Auth 流程'
            }
            
        except Exception as e:
            logger.error(f"發送 OTP 時發生錯誤：{str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_otp(self, verification_id: str, otp_code: str) -> dict:
        """
        驗證 OTP 代碼
        
        注意：本專案採用 6 位 OTP（verification_id + otp_code）為唯一流程。
        若在你的架構中需與 Firebase 前端驗證整合，請依實際需求調整此方法實作。
        
        Args:
            verification_id: Firebase 返回的驗證 session ID
            otp_code: 使用者輸入的驗證碼
        
        Returns:
            dict: {
                'success': bool,
                'phone_number': str (如果成功),
                'uid': str (Firebase user ID),
                'error': str (如果失敗)
            }
        """
        try:
            # 這裡提供一個簡化的實作範例
            logger.info(f"驗證 OTP：verification_id={verification_id}, code={otp_code}")
            
            # 模擬驗證（實際應對接你的 OTP 驗證機制）
            
            return {
                'success': True,
                'message': '此為模擬實作，請替換為實際的 OTP 驗證邏輯'
            }
        except Exception as e:
            logger.error(f"驗證 OTP 時發生錯誤：{str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_by_phone(self, phone_number: str):
        """
        根據手機號碼查詢 Firebase 使用者
        
        Args:
            phone_number: 完整手機號碼（包含國碼）
        
        Returns:
            UserRecord 或 None
        """
        try:
            user = auth.get_user_by_phone_number(phone_number)
            return user
        except auth.UserNotFoundError:
            logger.info(f"找不到手機號碼對應的 Firebase 使用者：{phone_number}")
            return None
        except Exception as e:
            logger.error(f"查詢 Firebase 使用者時發生錯誤：{str(e)}")
            return None


# 建立全域實例供其他模組使用
firebase_service = FirebaseAuthService()

