from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Application(models.Model):
    """證券帳號申請表單模型"""

    STATUS_CHOICES = [
        ('PENDING', '審核中'),
        ('APPROVED', '已通過'),
        ('REJECTED', '已拒絕'),
        ('ADDITIONAL_REQUIRED', '待補件'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', verbose_name='申請人')
    account_name = models.CharField(max_length=100, verbose_name='申請人帳號名稱', help_text='證券帳號的名稱')
    phone_number = models.CharField(max_length=20, verbose_name='電話號碼', help_text='聯絡用電話號碼')
    address = models.TextField(verbose_name='詳細地址', help_text='完整的聯絡地址')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name='申請狀態')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申請時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='最後更新時間')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='審核時間')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications', verbose_name='審核人員')
    rejection_reason = models.TextField(blank=True, verbose_name='拒絕原因', help_text='當申請被拒絕時填寫的原因')  # 拒絕原因（當 status 為 REJECTED 時使用）
    additional_info_required = models.TextField(blank=True, verbose_name='需補充資料說明', help_text='需要申請人補充的具體內容和原因')  # 補件說明（當 status 為 ADDITIONAL_REQUIRED 時使用）
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='通過時間')  # 通過時間（當status為 APPROVED 時自動設定）

    class Meta:
        verbose_name = '證券帳號申請'
        verbose_name_plural = '證券帳號申請'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.account_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """覆寫save方法，自動設定時間戳記"""
        # 如果狀態改為已通過，設定通過時間
        if self.status == 'APPROVED' and not self.approved_at:
            self.approved_at = timezone.now()

        # 如果狀態有變更（非PENDING），設定審核時間
        if self.status != 'PENDING' and not self.reviewed_at:
            self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def can_be_updated(self):
        """判斷申請是否可以被更新（只有待補件狀態可以更新）"""
        return self.status == 'ADDITIONAL_REQUIRED'

    @property
    def is_pending(self):
        """判斷是否為審核中狀態"""
        return self.status == 'PENDING'

    @property
    def is_approved(self):
        """判斷是否已通過"""
        return self.status == 'APPROVED'

    @property
    def is_rejected(self):
        """判斷是否已拒絕"""
        return self.status == 'REJECTED'
