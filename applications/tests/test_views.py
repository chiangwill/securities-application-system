from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from applications.models import Application


class ViewsTestCase(TestCase):
    """Views 測試基類"""

    def setUp(self):
        """設置測試資料"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', first_name='測試用戶')
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass123', is_staff=True, is_superuser=True)


class HomeViewTest(ViewsTestCase):
    """首頁 View 測試"""

    def test_home_view_anonymous_user(self):
        """測試未登入用戶訪問首頁"""

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '歡迎使用證券帳號申請系統')
        self.assertContains(response, '立即註冊')
        self.assertContains(response, '立即登入')

    def test_home_view_authenticated_user_redirects(self):
        """測試已登入用戶訪問首頁會重定向"""

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('application_status'))


class AuthenticationViewsTest(ViewsTestCase):
    """身份驗證 Views 測試"""

    def test_user_register_get(self):
        """測試註冊頁面 GET 請求"""

        response = self.client.get(reverse('user_register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '用戶註冊')

    def test_user_register_post_valid(self):
        """測試有效註冊 POST 請求"""

        data = {'username': 'newuser', 'first_name': '新用戶', 'email': 'newuser@example.com', 'password1': 'newpass123', 'password2': 'newpass123'}
        response = self.client.post(reverse('user_register'), data)
        self.assertRedirects(response, reverse('user_login'))

        # 檢查用戶是否已創建
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # 檢查成功訊息
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('註冊成功' in str(m) for m in messages))

    def test_user_register_authenticated_user_redirects(self):
        """測試已登入用戶訪問註冊頁面會重定向"""

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_register'))
        self.assertRedirects(response, reverse('application_status'))

    def test_user_login_get(self):
        """測試登入頁面 GET 請求"""

        response = self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '用戶登入')

    def test_user_login_post_valid(self):
        """測試有效登入 POST 請求"""

        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(reverse('user_login'), data)
        self.assertRedirects(response, reverse('application_status'))

    def test_user_login_post_invalid(self):
        """測試無效登入 POST 請求"""

        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(reverse('user_login'), data)
        self.assertEqual(response.status_code, 200)

        # 檢查錯誤訊息
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('帳號或密碼錯誤' in str(m) for m in messages))

    def test_user_logout(self):
        """測試登出"""

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('home'))

        # 檢查登出訊息
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('成功登出' in str(m) for m in messages))


class ApplicationViewsTest(ViewsTestCase):
    """申請相關 Views 測試"""

    def test_application_create_get_no_existing_application(self):
        """測試創建申請頁面 - 沒有現有申請"""

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '證券帳戶申請表單')

    def test_application_create_get_with_existing_application(self):
        """測試創建申請頁面 - 已有申請會重定向"""

        # 創建現有申請
        Application.objects.create(user=self.user, account_name='existing_account', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_create'))
        self.assertRedirects(response, reverse('application_status'))

    def test_application_create_post_valid(self):
        """測試有效申請提交"""

        self.client.login(username='testuser', password='testpass123')
        data = {'account_name': 'test_account_001', 'phone_number': '0912-345-678', 'address': '台北市信義區信義路五段7號'}
        response = self.client.post(reverse('application_create'), data)
        self.assertRedirects(response, reverse('application_status'))

        # 檢查申請是否已創建
        self.assertTrue(Application.objects.filter(user=self.user).exists())

    def test_application_create_requires_login(self):
        """測試創建申請需要登入"""

        response = self.client.get(reverse('application_create'))
        self.assertRedirects(response, '/accounts/login/?next=/application/create/')

    def test_application_status_no_application_shows_welcome(self):
        """測試查看狀態 - 沒有申請顯示歡迎頁面"""

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_status'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '歡迎來到證券帳號申請系統')
        self.assertContains(response, '立即申請證券帳戶')
        self.assertContains(response, '填寫申請表單')
        self.assertContains(response, '等待審核')
        # 檢查此時 application 變數是 None
        self.assertIsNone(response.context['application'])

    def test_application_status_with_application(self):
        """測試查看狀態 - 有申請正常顯示"""

        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_status'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_account_001')
        self.assertContains(response, '審核中')
        # 檢查此時 application 變數不是 None
        self.assertIsNotNone(response.context['application'])
        self.assertEqual(response.context['application'], application)

    def test_application_update_get_valid_status(self):
        """測試更新申請 - 待補件狀態"""

        application = Application.objects.create(user=self.user,
                                                 account_name='test_account_001',
                                                 phone_number='0912-345-678',
                                                 address='台北市信義區信義路五段7號',
                                                 status='ADDITIONAL_REQUIRED',
                                                 additional_info_required='請提供更詳細的地址')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_update', args=[application.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '補充申請資料')

    def test_application_update_invalid_status_redirects(self):
        """測試更新申請 - 非待補件狀態會重定向"""

        application = Application.objects.create(
            user=self.user,
            account_name='test_account_001',
            phone_number='0912-345-678',
            address='台北市信義區信義路五段7號',
            status='PENDING'  # 不是 ADDITIONAL_REQUIRED
        )

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_update', args=[application.id]))
        self.assertRedirects(response, reverse('application_status'))

    def test_application_update_post_valid(self):
        """測試有效更新申請"""

        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='ADDITIONAL_REQUIRED')

        self.client.login(username='testuser', password='testpass123')
        data = {'account_name': 'updated_account', 'phone_number': '0912-999-888', 'address': '台北市大安區敦化南路二段100號'}
        response = self.client.post(reverse('application_update', args=[application.id]), data)
        self.assertRedirects(response, reverse('application_status'))

        # 檢查申請是否已更新且狀態重置為 PENDING
        application.refresh_from_db()
        self.assertEqual(application.account_name, 'updated_account')
        self.assertEqual(application.status, 'PENDING')

    def test_application_success_approved_status(self):
        """測試成功頁面 - 已通過狀態"""

        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='APPROVED')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_success', args=[application.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '恭喜！申請已通過')

    def test_application_success_non_approved_status_redirects(self):
        """測試成功頁面 - 非已通過狀態會重定向"""

        application = Application.objects.create(user=self.user, account_name='test_account_001', phone_number='0912-345-678', address='台北市信義區信義路五段7號', status='PENDING')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_success', args=[application.id]))
        self.assertRedirects(response, reverse('application_status'))

    def test_user_can_only_access_own_application(self):
        """測試用戶只能訪問自己的申請"""

        # 創建另一個用戶和申請
        other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='otherpass123')
        other_application = Application.objects.create(user=other_user, account_name='other_account', phone_number='0912-111-222', address='高雄市前金區中正四路100號')

        # 用第一個用戶嘗試訪問第二個用戶的申請
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_update', args=[other_application.id]))
        self.assertEqual(response.status_code, 404)
