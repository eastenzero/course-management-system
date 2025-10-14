from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关 - 支持 /api/v1/auth/ 路径
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', views.UserProfileView.as_view(), name='current_user'),  # 当前用户信息
    path('register/', views.RegisterView.as_view(), name='register'),

    # 认证相关 - 兼容原有路径
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/logout/', views.logout_view, name='auth_logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('auth/register/', views.RegisterView.as_view(), name='auth_register'),

    # 用户资料
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('preferences/', views.UserPreferenceView.as_view(), name='preferences'),

    # 用户管理（管理员）
    path('', views.UserListCreateView.as_view(), name='user_list_create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
