"""
手機驗證相關的資料模型

此檔案定義了使用者手機驗證所需的資料表欄位。
可以直接複製到現有的 Django User Model 中，或作為獨立的 Profile Model。
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid

# 為手機驗證而新增的 user data DB 欄位
class CustomUser(AbstractUser):
    """
    擴展 Django 原生 User Model，新增手機驗證相關欄位
    
    如果你的專案已有 User Model，請將以下欄位複製到你的 Model 中。
    """
    
    # 手機號碼（包含國碼，例如：+886987654321）
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+\d{1,3}\d{4,14}$',
                message='手機號碼格式應為：+國碼號碼（例如：+886987654321）'
            )
        ],
        verbose_name='手機號碼',
        help_text='完整的手機號碼，包含國碼（例如：+886987654321）'
    )
    
    # 手機號碼是否已驗證
    phone_verified = models.BooleanField(
        default=False,
        verbose_name='手機已驗證',
        help_text='使用者是否已完成手機號碼驗證'
    )
    
    # OTP 驗證嘗試次數
    otp_attempts = models.IntegerField(
        default=0,
        verbose_name='OTP 嘗試次數',
        help_text='當前 verification session 的驗證嘗試次數（最多3次）'
    )
    
    # 當前驗證狀態
    class VerificationStatus(models.TextChoices):
        OTP_SENT = 'OTP_SENT', 'OTP 已發送'
        OTP_RESENT = 'OTP_RESENT', 'OTP 已重新發送'
        VERIFIED = 'VERIFIED', '已驗證'
        INVALID_OTP = 'INVALID_OTP', '驗證碼錯誤'
        LOCKED = 'LOCKED', '已鎖定（錯誤次數過多）'
        TOO_MANY_REQUESTS = 'TOO_MANY_REQUESTS', '請求過於頻繁'
    
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        blank=True,
        null=True,
        verbose_name='驗證狀態',
        help_text='當前的手機驗證狀態'
    )
    
    # Firebase 驗證 ID（用於 OTP 驗證）
    verification_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Firebase Verification ID',
        help_text='Firebase 返回的驗證 session ID'
    )
    
    # 最後一次發送 OTP 的時間（用於 rate limiting）
    last_otp_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='最後發送時間',
        help_text='最後一次發送 OTP 的時間戳記'
    )
    
    # ============================================================
    # User Profile 相關欄位
    # ============================================================
    
    nickname = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='暱稱',
        help_text='使用者暱稱'
    )
    
    gender = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name='性別',
        help_text='使用者性別'
    )
    
    age = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='年齡',
        help_text='使用者年齡'
    )
    
    degree = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='學歷',
        help_text='使用者學歷'
    )
    
    counseling_record = models.IntegerField(
        default=0,
        verbose_name='諮商記錄數',
        help_text='諮商記錄數量'
    )
    
    motivation_1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='動機1',
        help_text='使用者動機1'
    )
    
    motivation_2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='動機2',
        help_text='使用者動機2'
    )
    
    motivation_3 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='動機3',
        help_text='使用者動機3'
    )
    
    on_stage = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='上線狀態',
        help_text='使用者上線狀態'
    )
    
    status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='狀態',
        help_text='使用者狀態'
    )
    
    retry_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='重試時間',
        help_text='重試時間戳記'
    )
    
    monkey_try = models.IntegerField(
        default=0,
        verbose_name='Monkey 嘗試次數',
        help_text='Monkey 嘗試次數'
    )
    
    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者列表'
    
    def __str__(self):
        return self.username
    
    def reset_otp_attempts(self):
        """重置 OTP 嘗試次數"""
        self.otp_attempts = 0
        self.save(update_fields=['otp_attempts'])
    
    def increment_otp_attempts(self):
        """增加 OTP 嘗試次數，如果達到3次則鎖定"""
        self.otp_attempts += 1
        if self.otp_attempts >= 3:
            self.verification_status = self.VerificationStatus.LOCKED
        self.save(update_fields=['otp_attempts', 'verification_status'])


class OTPVerificationLog(models.Model):
    """
    OTP 驗證記錄表（可選）
    
    用於記錄所有 OTP 發送與驗證的歷史，方便追蹤與除錯。
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='otp_logs',
        verbose_name='使用者'
    )
    
    phone_number = models.CharField(
        max_length=20,
        verbose_name='手機號碼'
    )
    
    action = models.CharField(
        max_length=20,
        choices=[
            ('SEND', '發送 OTP'),
            ('RESEND', '重新發送 OTP'),
            ('VERIFY_SUCCESS', '驗證成功'),
            ('VERIFY_FAILED', '驗證失敗'),
        ],
        verbose_name='操作類型'
    )
    
    verification_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Verification ID'
    )
    
    success = models.BooleanField(
        default=False,
        verbose_name='是否成功'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='錯誤訊息'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )
    
    class Meta:
        verbose_name = 'OTP 驗證記錄'
        verbose_name_plural = 'OTP 驗證記錄列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"

