import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Application


class ApplicationForm(forms.ModelForm):
    """證券帳號申請表單"""

    class Meta:
        model = Application
        fields = ['account_name', 'phone_number', 'address']

        labels = {
            'account_name': '申請人帳號名稱',
            'phone_number': '電話號碼',
            'address': '詳細地址',
        }

        help_texts = {
            'account_name': '證券帳號的名稱，3-20個字符，只能包含英文字母、數字、底線、短橫線',
            'phone_number': '請輸入有效的台灣手機號碼',
            'address': '請提供完整的聯絡地址',
        }

        widgets = {
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：john_doe_001'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：0912-345-678'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '請輸入完整地址，包含郵遞區號、縣市、區域、街道門牌'
            }),
        }

    def clean_account_name(self):
        """驗證帳號名稱格式和唯一性"""
        account_name = self.cleaned_data['account_name']

        # 格式驗證
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', account_name):
            raise ValidationError('帳號名稱只能包含英文字母、數字、底線、短橫線，且必須以字母或數字開頭')

        if len(account_name) < 3:
            raise ValidationError('帳號名稱至少需要3個字符')

        if len(account_name) > 20:
            raise ValidationError('帳號名稱不能超過20個字符')

        # 唯一性驗證 - 檢查整個系統中是否已存在
        existing_application = Application.objects.filter(account_name=account_name)

        # 如果是更新表單，排除自己
        if self.instance.pk:
            existing_application = existing_application.exclude(pk=self.instance.pk)

        if existing_application.exists():
            raise ValidationError('此帳號名稱已被使用，請選擇其他名稱')

        return account_name

    def clean_phone_number(self):
        """驗證手機號碼格式"""

        phone_number = self.cleaned_data['phone_number']

        # 移除所有空格和短橫線，方便驗證
        cleaned_phone = re.sub(r'[\s\-()]', '', phone_number)

        # 台灣手機號碼格式：09XXXXXXXX
        mobile_pattern = r'^09\d{8}$'

        if not re.match(mobile_pattern, cleaned_phone):
            raise ValidationError('請輸入有效的台灣手機號碼格式，例如：0912-345-678')

        return phone_number

    def clean_address(self):
        """驗證地址內容"""
        address = self.cleaned_data['address'].strip()

        if len(address) < 10:
            raise ValidationError('地址太短，請提供完整的聯絡地址')

        if len(address) > 200:
            raise ValidationError('地址過長，請簡化至200個字符以內')

        # 檢查是否包含基本地址元素
        if not any(keyword in address for keyword in ['市', '縣', '區', '鄉', '鎮', '路', '街', '巷', '號']):
            raise ValidationError('請提供完整的地址資訊，包含縣市、區域、街道門牌')

        return address


class ApplicationUpdateForm(ApplicationForm):
    """補件時的申請更新表單"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 在補件時，可以在表單上方顯示需要補充的資訊
        if self.instance and self.instance.additional_info_required:
            for field_name, field in self.fields.items():
                field.help_text = f"{field.help_text or ''}\n補件說明：{self.instance.additional_info_required}"


class CustomUserCreationForm(UserCreationForm):
    """自定義使用者註冊表單"""

    email = forms.EmailField(required=True, label='電子郵件', help_text='請輸入有效的電子郵件地址', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}))

    first_name = forms.CharField(max_length=30, required=True, label='姓名', help_text='請輸入您的真實姓名', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '王小明'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')
        labels = {
            'username': '使用者帳號',
        }
        help_texts = {
            'username': '請設定您的登入帳號，只能包含字母、數字和 @/./+/-/_ 符號',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 自定義中文化標籤和說明
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': '請輸入使用者帳號'})
        self.fields['password1'].label = '密碼'
        self.fields['password1'].help_text = '密碼至少8個字符，不能完全是數字'
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '請輸入密碼'})
        self.fields['password2'].label = '確認密碼'
        self.fields['password2'].help_text = '請再次輸入相同的密碼以確認'
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '請再次輸入密碼'})

    def clean_email(self):
        """驗證電子郵件唯一性"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('此電子郵件已被註冊，請使用其他郵件地址')
        return email

    def clean_username(self):
        """驗證使用者名稱"""
        username = self.cleaned_data['username']
        if len(username) < 3:
            raise ValidationError('使用者帳號至少需要3個字符')
        if len(username) > 150:
            raise ValidationError('使用者帳號不能超過150個字符')
        return username

    def save(self, commit=True):
        """儲存使用者資料"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """自定義登入表單"""

    username = forms.CharField(max_length=150, label='使用者帳號', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請輸入使用者帳號', 'autofocus': True}))
    password = forms.CharField(label='密碼', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '請輸入密碼'}))
