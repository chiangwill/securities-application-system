from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from applications.admin import ApplicationAdmin
from applications.models import Application


class ApplicationAdminTest(TestCase):
    """ApplicationAdmin 測試"""

    def setUp(self):
        """設置測試資料"""
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass123', is_staff=True, is_superuser=True)
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.site = AdminSite()
        self.admin = ApplicationAdmin(Application, self.site)

    def test_list_display(self):
        """測試列表顯示欄位"""
        expected_fields = ['id', 'user', 'account_name', 'phone_number', 'colored_status', 'created_at', 'reviewed_at', 'reviewed_by']
        self.assertEqual(list(self.admin.list_display), expected_fields)

    def test_list_filter(self):
        """測試列表篩選器"""
        expected_filters = ['status', 'created_at', 'reviewed_at', 'reviewed_by']
        self.assertEqual(list(self.admin.list_filter), expected_filters)

    def test_search_fields(self):
        """測試搜尋欄位"""
        expected_fields = ['user__username', 'user__email', 'account_name', 'phone_number', 'address']
        self.assertEqual(list(self.admin.search_fields), expected_fields)

    def test_colored_status_method(self):
        """測試狀態顏色顯示方法"""
        application = Application.objects.create(user=self.user, account_name='test_account', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='PENDING')

        colored_status = self.admin.colored_status(application)
        self.assertIn('審核中', colored_status)
        self.assertIn('#ffc107', colored_status)  # 黃色
        self.assertIn('font-weight: bold', colored_status)

    def test_save_model_sets_reviewed_by(self):
        """測試保存模型時自動設定審核人員"""
        application = Application.objects.create(user=self.user, account_name='test_account', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='PENDING')

        # 模擬 admin 編輯申請
        request = self.factory.post('/admin/')
        request.user = self.admin_user

        # 添加 messages framework 支援
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        # 改變狀態並保存
        application.status = 'APPROVED'
        self.admin.save_model(request, application, None, True)

        application.refresh_from_db()
        self.assertEqual(application.reviewed_by, self.admin_user)

    def test_approve_applications_action(self):
        """測試批量通過申請動作"""
        # 創建待審核申請
        applications = [Application.objects.create(user=self.user, account_name=f'test_account_{i}', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='PENDING') for i in range(3)]

        request = self.factory.post('/admin/')
        request.user = self.admin_user
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        queryset = Application.objects.filter(status='PENDING')
        self.admin.approve_applications(request, queryset)

        # 檢查所有申請都被通過
        for app in applications:
            app.refresh_from_db()
            self.assertEqual(app.status, 'APPROVED')
            self.assertEqual(app.reviewed_by, self.admin_user)

    def test_reject_applications_action(self):
        """測試批量拒絕申請動作"""
        # 創建待審核申請
        applications = [Application.objects.create(user=self.user, account_name=f'test_account_{i}', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='PENDING') for i in range(2)]

        request = self.factory.post('/admin/')
        request.user = self.admin_user
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        queryset = Application.objects.filter(status='PENDING')
        self.admin.reject_applications(request, queryset)

        # 檢查所有申請都被拒絕
        for app in applications:
            app.refresh_from_db()
            self.assertEqual(app.status, 'REJECTED')
            self.assertEqual(app.reviewed_by, self.admin_user)
            self.assertEqual(app.rejection_reason, '批量拒絕操作')

    def test_get_queryset_optimization(self):
        """測試查詢集優化"""
        request = self.factory.get('/admin/')
        request.user = self.admin_user

        queryset = self.admin.get_queryset(request)

        # 檢查是否有進行 select_related 優化
        self.assertIn('user', queryset.query.select_related)
        self.assertIn('reviewed_by', queryset.query.select_related)

    def test_readonly_fields(self):
        """測試唯讀欄位"""
        expected_readonly = ['created_at', 'updated_at', 'reviewed_at', 'approved_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)

    def test_fieldsets_configuration(self):
        """測試欄位分組配置"""
        fieldsets = self.admin.fieldsets

        # 檢查有四個分組
        self.assertEqual(len(fieldsets), 4)

        # 檢查分組名稱
        group_names = [fieldset[0] for fieldset in fieldsets]
        expected_names = ['申請人資訊', '審核資訊', '審核意見', '時間記錄']
        self.assertEqual(group_names, expected_names)

        # 檢查申請人資訊包含的欄位
        applicant_info_fields = fieldsets[0][1]['fields']
        expected_applicant_fields = ('user', 'account_name', 'phone_number', 'address')
        self.assertEqual(applicant_info_fields, expected_applicant_fields)
