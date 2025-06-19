from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from applications.forms import (
    ApplicationForm,
    ApplicationUpdateForm,
    CustomUserCreationForm,
    LoginForm,
)
from applications.models import Application


class ApplicationFormTest(TestCase):
    """ApplicationForm 測試"""

    def setUp(self):
        """設置測試資料"""
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.valid_data = {'account_name': 'test_account_001', 'phone_number': '0912-345-678', 'address': '台北市信義區信義路五段7號'}

    def test_valid_form(self):
        """測試有效表單"""

        form = ApplicationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_account_name_validation_format(self):
        """測試帳號名稱格式驗證"""

        # 測試無效格式
        invalid_names = [
            '_test',  # 不能以底線開頭
            '-test',  # 不能以短橫線開頭
            'test@123',  # 不能包含特殊字符
            'test 123',  # 不能包含空格
            'ab',  # 太短
            'a' * 21,  # 太長
        ]

        for invalid_name in invalid_names:
            data = self.valid_data.copy()
            data['account_name'] = invalid_name
            form = ApplicationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('account_name', form.errors)

    def test_account_name_uniqueness(self):
        """測試帳號名稱唯一性"""

        # 創建一個申請
        Application.objects.create(user=self.user, account_name='existing_account', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        # 嘗試創建相同帳號名稱
        data = self.valid_data.copy()
        data['account_name'] = 'existing_account'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('account_name', form.errors)

    def test_phone_number_validation(self):
        """測試電話號碼驗證"""

        # 有效的電話號碼
        valid_phones = [
            '0912345678',
            '0912-345-678',
        ]

        for valid_phone in valid_phones:
            data = self.valid_data.copy()
            data['phone_number'] = valid_phone
            form = ApplicationForm(data=data)
            self.assertTrue(form.is_valid(), f"Should be valid: {valid_phone}")

        # 無效的電話號碼
        invalid_phones = [
            '1234567890',  # 不是台灣格式
            '0812345678',  # 不是09開頭的手機
            '091234567',  # 手機號碼太短
            '09123456789',  # 手機號碼太長
        ]

        for invalid_phone in invalid_phones:
            data = self.valid_data.copy()
            data['phone_number'] = invalid_phone
            form = ApplicationForm(data=data)
            self.assertFalse(form.is_valid(), f"Should be invalid: {invalid_phone}")
            self.assertIn('phone_number', form.errors)

    def test_address_validation(self):
        """測試地址驗證"""

        # 地址太短
        data = self.valid_data.copy()
        data['address'] = '台北市'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)

        # 地址太長
        data['address'] = 'a' * 201
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)

        # 地址不完整（缺少關鍵字）
        data['address'] = '某個地方的某個位置'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)


class ApplicationUpdateFormTest(TestCase):
    """ApplicationUpdateForm 測試"""

    def setUp(self):
        """設置測試資料"""

        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.application = Application.objects.create(user=self.user,
                                                      account_name='test_account_001',
                                                      phone_number='0912-345-678',
                                                      address='台北市信義區信義路五段7號',
                                                      status='ADDITIONAL_REQUIRED',
                                                      additional_info_required='請提供更詳細的地址資訊')

    def test_update_form_inherits_from_application_form(self):
        """測試更新表單繼承自申請表單"""

        form = ApplicationUpdateForm(instance=self.application)
        self.assertIsInstance(form, ApplicationForm)

    def test_form_with_additional_info(self):
        """測試包含補件說明的表單"""

        form = ApplicationUpdateForm(instance=self.application)
        # 檢查 help_text 是否包含補件說明
        for field in form.fields.values():
            if field.help_text:
                self.assertIn(self.application.additional_info_required, field.help_text)


class CustomUserCreationFormTest(TestCase):
    """CustomUserCreationForm 測試"""

    def setUp(self):
        """設置測試資料"""

        self.valid_data = {'username': 'testuser', 'first_name': '測試用戶', 'email': 'test@example.com', 'password1': 'testpass123', 'password2': 'testpass123'}

    def test_valid_form(self):
        """測試有效表單"""

        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_email_uniqueness(self):
        """測試電子郵件唯一性"""

        # 創建一個用戶
        User.objects.create_user(username='existing', email='existing@example.com', password='testpass123')

        # 嘗試使用相同郵件註冊
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        data['username'] = 'newuser'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_username_validation(self):
        """測試使用者名稱驗證"""

        # 用戶名太短
        data = self.valid_data.copy()
        data['username'] = 'ab'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_save(self):
        """測試表單保存"""

        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, '測試用戶')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))


class LoginFormTest(TestCase):
    """LoginForm 測試"""

    def test_valid_form(self):
        """測試有效登入表單"""

        form_data = {'username': 'testuser', 'password': 'testpass123'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_form(self):
        """測試空表單"""

        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
