from django.urls import path

from applications import views

urlpatterns = [
    # 首頁
    path('', views.home, name='home'),

    # 身份驗證
    path('accounts/register/', views.user_register, name='user_register'),
    path('accounts/login/', views.user_login, name='user_login'),
    path('accounts/logout/', views.user_logout, name='user_logout'),

    # 申請流程
    path('application/create/', views.application_create, name='application_create'),
    path('application/status/', views.application_status, name='application_status'),
    path('application/update/<int:application_id>/', views.application_update, name='application_update'),
    path('application/success/<int:application_id>/', views.application_success, name='application_success'),
]
