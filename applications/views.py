from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    ApplicationForm,
    ApplicationUpdateForm,
    CustomUserCreationForm,
    LoginForm,
)
from .models import Application


def home(request):
    """首頁 - 根據登入狀態導向不同頁面"""

    if request.user.is_authenticated:
        # 已登入用戶導向申請狀態頁面
        return redirect('application_status')
    else:
        # 未登入用戶顯示登入/註冊選項
        return render(request, 'applications/home.html')


def user_register(request):
    """使用者註冊"""

    if request.user.is_authenticated:
        return redirect('application_status')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'帳號 {username} 註冊成功！請登入開始申請證券帳戶。')
            return redirect('user_login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'applications/register.html', {'form': form})


def user_login(request):
    """使用者登入"""

    if request.user.is_authenticated:
        return redirect('application_status')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'歡迎回來，{user.first_name or user.username}！')
                return redirect('application_status')
            else:
                messages.error(request, '帳號或密碼錯誤，請重新輸入。')
    else:
        form = LoginForm()

    return render(request, 'applications/login.html', {'form': form})


def user_logout(request):
    """使用者登出"""

    logout(request)
    messages.info(request, '您已成功登出。')
    return redirect('home')


@login_required
def application_create(request):
    """創建證券帳戶申請"""

    # 檢查用戶是否已有申請
    try:
        existing_application = Application.objects.get(user=request.user)
        messages.info(request, '您已有一個申請記錄，請查看申請狀態。')
        return redirect('application_status')
    except Application.DoesNotExist:
        pass  # 沒有現有申請，可以繼續創建

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()

            messages.success(request, '證券帳戶申請已成功提交！我們會盡快處理您的申請。')
            return redirect('application_status')
    else:
        form = ApplicationForm()

    return render(request, 'applications/create.html', {'form': form})


@login_required
def application_status(request):
    """查看申請狀態"""

    try:
        application = Application.objects.get(user=request.user)
    except Application.DoesNotExist:
        messages.info(request, '您尚未提交申請，請先填寫申請表單。')
        return redirect('application_create')

    context = {
        'application': application,
    }

    return render(request, 'applications/status.html', context)


@login_required
def application_update(request, application_id):
    """更新申請（補件功能）"""

    # 確保只能更新自己的申請
    application = get_object_or_404(Application, id=application_id, user=request.user)

    # 只有「待補件」狀態才能更新
    if not application.can_be_updated:
        messages.error(request, '此申請目前無法修改。只有「待補件」狀態的申請可以更新。')
        return redirect('application_status')

    if request.method == 'POST':
        form = ApplicationUpdateForm(request.POST, instance=application)
        if form.is_valid():
            # 更新申請並重置狀態為 PENDING
            application = form.save(commit=False)
            application.status = 'PENDING'
            application.reviewed_at = None
            application.reviewed_by = None
            application.additional_info_required = ''  # 清除補件說明
            application.save()

            messages.success(request, '申請資料已更新並重新提交審核。感謝您提供補充資料！')
            return redirect('application_status')
    else:
        form = ApplicationUpdateForm(instance=application)

    context = {
        'form': form,
        'application': application,
    }

    return render(request, 'applications/update.html', context)


@login_required
def application_success(request, application_id):
    """申請通過的恭喜頁面"""

    # 確保只能查看自己的申請
    application = get_object_or_404(Application, id=application_id, user=request.user)

    # 只有已通過的申請才能查看此頁面
    if not application.is_approved:
        messages.error(request, '此申請尚未通過審核。')
        return redirect('application_status')

    context = {
        'application': application,
    }

    return render(request, 'applications/success.html', context)


# 錯誤處理頁面
def handler404(request, exception):
    """404錯誤處理"""

    return render(request, 'applications/404.html', status=404)


def handler500(request):
    """500錯誤處理"""

    return render(request, 'applications/500.html', status=500)
