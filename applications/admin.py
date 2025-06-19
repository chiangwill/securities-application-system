from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """證券帳號申請的Admin管理介面"""

    # 列表頁面顯示的欄位
    list_display = ['id', 'user', 'account_name', 'phone_number', 'colored_status', 'created_at', 'reviewed_at', 'reviewed_by']

    # 列表頁面的篩選器
    list_filter = ['status', 'created_at', 'reviewed_at', 'reviewed_by']

    # 搜尋欄位
    search_fields = ['user__username', 'user__email', 'account_name', 'phone_number', 'address']

    # 詳細頁面的欄位分組
    fieldsets = (
        ('申請人資訊', {
            'fields': ('user', 'account_name', 'phone_number', 'address')
        }),
        ('審核資訊', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'approved_at')
        }),
        (
            '審核意見',
            {
                'fields': ('rejection_reason', 'additional_info_required'),
                'classes': ('collapse', ),  # 預設收起
            }),
        ('時間記錄', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', ),
        }),
    )

    # 唯讀欄位
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at', 'approved_at']

    # 列表頁面每頁顯示數量
    list_per_page = 25

    # 預設排序
    ordering = ['-created_at']

    # 日期層次導航
    date_hierarchy = 'created_at'

    def colored_status(self, obj):
        """為狀態添加顏色標示"""
        colors = {
            'PENDING': '#ffc107',  # 黃色 - 等待中
            'APPROVED': '#28a745',  # 綠色 - 已通過
            'REJECTED': '#dc3545',  # 紅色 - 已拒絕
            'ADDITIONAL_REQUIRED': '#17a2b8',  # 藍色 - 待補件
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())

    colored_status.short_description = '申請狀態'
    colored_status.admin_order_field = 'status'

    def save_model(self, request, obj, form, change):
        """覆寫save_model，自動設定審核人員"""
        if change:  # 如果是編輯現有物件
            original = Application.objects.get(pk=obj.pk)
            # 如果狀態有變更且不是PENDING，設定審核人員
            if (original.status != obj.status and obj.status != 'PENDING' and not obj.reviewed_by):
                obj.reviewed_by = request.user

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """優化查詢，減少資料庫查詢次數"""
        return super().get_queryset(request).select_related('user', 'reviewed_by')

    # 自定義Admin動作
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        """批量通過申請"""
        count = 0
        for application in queryset.filter(status='PENDING'):
            application.status = 'APPROVED'
            application.reviewed_by = request.user
            application.save()
            count += 1

        self.message_user(request, f'成功通過 {count} 個申請。')

    approve_applications.short_description = '批量通過選中的申請'

    def reject_applications(self, request, queryset):
        """批量拒絕申請"""
        count = 0
        for application in queryset.filter(status='PENDING'):
            application.status = 'REJECTED'
            application.reviewed_by = request.user
            application.rejection_reason = '批量拒絕操作'
            application.save()
            count += 1

        self.message_user(request, f'成功拒絕 {count} 個申請。')

    reject_applications.short_description = '批量拒絕選中的申請'

    class Media:
        css = {'all': ('admin/css/custom_admin.css', )}
