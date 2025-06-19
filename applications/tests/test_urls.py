from django.test import TestCase
from django.urls import resolve, reverse

from applications import views


class URLsTest(TestCase):
    """URLs 配置測試"""

    def test_home_url(self):
        """測試首頁 URL"""
        url = reverse('home')
        self.assertEqual(url, '/')
        self.assertEqual(resolve(url).func, views.home)

    def test_user_register_url(self):
        """測試註冊 URL"""
        url = reverse('user_register')
        self.assertEqual(url, '/accounts/register/')
        self.assertEqual(resolve(url).func, views.user_register)

    def test_user_login_url(self):
        """測試登入 URL"""
        url = reverse('user_login')
        self.assertEqual(url, '/accounts/login/')
        self.assertEqual(resolve(url).func, views.user_login)

    def test_user_logout_url(self):
        """測試登出 URL"""
        url = reverse('user_logout')
        self.assertEqual(url, '/accounts/logout/')
        self.assertEqual(resolve(url).func, views.user_logout)

    def test_application_create_url(self):
        """測試創建申請 URL"""
        url = reverse('application_create')
        self.assertEqual(url, '/application/create/')
        self.assertEqual(resolve(url).func, views.application_create)

    def test_application_status_url(self):
        """測試申請狀態 URL"""
        url = reverse('application_status')
        self.assertEqual(url, '/application/status/')
        self.assertEqual(resolve(url).func, views.application_status)

    def test_application_update_url(self):
        """測試更新申請 URL"""
        url = reverse('application_update', args=[1])
        self.assertEqual(url, '/application/update/1/')
        self.assertEqual(resolve(url).func, views.application_update)

    def test_application_success_url(self):
        """測試成功頁面 URL"""
        url = reverse('application_success', args=[1])
        self.assertEqual(url, '/application/success/1/')
        self.assertEqual(resolve(url).func, views.application_success)

    def test_url_names_exist(self):
        """測試所有 URL 名稱都存在"""
        url_names = ['home', 'user_register', 'user_login', 'user_logout', 'application_create', 'application_status', 'application_update', 'application_success']

        for name in url_names:
            try:
                if name in ['application_update', 'application_success']:
                    reverse(name, args=[1])
                else:
                    reverse(name)
            except Exception as e:
                self.fail(f"URL name '{name}' failed: {e}")
