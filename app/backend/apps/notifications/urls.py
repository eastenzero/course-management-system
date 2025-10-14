"""
通知系统URL配置
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # 通知列表和详情
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # 通知操作
    path('mark-read/', views.mark_notifications_read, name='mark-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
    
    # 通知偏好设置
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
    
    # 管理员功能
    path('templates/', views.NotificationTemplateListView.as_view(), name='template-list'),
    path('create/', views.create_notification, name='create-notification'),
]
