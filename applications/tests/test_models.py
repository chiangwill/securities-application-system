from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from applications.models import Application


class ApplicationModelTest(TestCase):
    """Application 模型測試"""

    def setUp(self):
        """設置測試資料"""
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', first_name='測試用戶')
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass123', is_staff=True)

    def test_application_creation(self):
        """測試申請創建"""
        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        self.assertEqual(application.user, self.user)
        self.assertEqual(application.account_name, 'test_account_001')
        self.assertEqual(application.phone_number, '0912-345-678')
        self.assertEqual(application.status, 'PENDING')
        self.assertIsNotNone(application.created_at)
        self.assertIsNone(application.approved_at)
        self.assertTrue(application.is_pending)
        self.assertFalse(application.is_approved)

    def test_application_str_method(self):
        """測試字串表示方法"""
        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        expected_str = f"testuser - test_account_001 (審核中)"
        self.assertEqual(str(application), expected_str)

    def test_application_status_properties(self):
        """測試狀態屬性方法"""
        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        # 測試 PENDING 狀態
        self.assertTrue(application.is_pending)
        self.assertFalse(application.is_approved)
        self.assertFalse(application.is_rejected)
        self.assertFalse(application.can_be_updated)

        # 測試 APPROVED 狀態
        application.status = 'APPROVED'
        application.save()
        self.assertFalse(application.is_pending)
        self.assertTrue(application.is_approved)
        self.assertFalse(application.is_rejected)
        self.assertFalse(application.can_be_updated)

        # 測試 REJECTED 狀態
        application.status = 'REJECTED'
        application.save()
        self.assertFalse(application.is_pending)
        self.assertFalse(application.is_approved)
        self.assertTrue(application.is_rejected)
        self.assertFalse(application.can_be_updated)

        # 測試 ADDITIONAL_REQUIRED 狀態
        application.status = 'ADDITIONAL_REQUIRED'
        application.save()
        self.assertFalse(application.is_pending)
        self.assertFalse(application.is_approved)
        self.assertFalse(application.is_rejected)
        self.assertTrue(application.can_be_updated)

    def test_application_save_method_approved_timestamp(self):
        """測試保存方法 - 通過時間戳記"""
        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        # 初始狀態不應該有通過時間
        self.assertIsNone(application.approved_at)

        # 改為通過狀態
        application.status = 'APPROVED'
        application.save()

        # 應該自動設定通過時間
        self.assertIsNotNone(application.approved_at)
        self.assertAlmostEqual(application.approved_at, timezone.now(), delta=timezone.timedelta(seconds=5))

    def test_application_save_method_reviewed_timestamp(self):
        """測試保存方法 - 審核時間戳記"""
        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        # 初始狀態不應該有審核時間
        self.assertIsNone(application.reviewed_at)

        # 改為非 PENDING 狀態
        application.status = 'APPROVED'
        application.save()

        # 應該自動設定審核時間
        self.assertIsNotNone(application.reviewed_at)
        self.assertAlmostEqual(application.reviewed_at, timezone.now(), delta=timezone.timedelta(seconds=5))

    def test_application_ordering(self):
        """測試排序（最新的在前）"""
        # 創建多個申請
        app1 = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')

        app2 = Application.objects.create(user=user2, account_name='test_account_002', phone_number='0912-345-679', address='台北市大安區敦化南路二段100號')

        # 檢查排序
        applications = list(Application.objects.all())
        self.assertEqual(applications[0], app2)  # 最新的在前
        self.assertEqual(applications[1], app1)
