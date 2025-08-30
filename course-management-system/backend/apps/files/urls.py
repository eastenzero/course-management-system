"""
文件管理URL配置
"""

from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # 文件管理
    path('', views.FileListCreateView.as_view(), name='file_list_create'),
    path('<uuid:pk>/', views.FileDetailView.as_view(), name='file_detail'),
    path('<uuid:file_id>/download/', views.download_file, name='download_file'),
    
    # 文件分享
    path('shares/', views.FileShareListCreateView.as_view(), name='file_share_list_create'),
    path('share/<str:share_token>/', views.access_shared_file, name='access_shared_file'),
    
    # 统计和批量操作
    path('statistics/', views.file_statistics, name='file_statistics'),
    path('bulk-operation/', views.bulk_file_operation, name='bulk_file_operation'),
]
