from django.urls import path
from . import views

app_name = 'classrooms'

urlpatterns = [
    # 教学楼管理
    path('buildings/', views.BuildingListCreateView.as_view(), name='building_list_create'),
    path('buildings/<int:pk>/', views.BuildingDetailView.as_view(), name='building_detail'),
    
    # 教室管理
    path('', views.ClassroomListCreateView.as_view(), name='classroom_list_create'),
    path('<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    
    # 教室功能
    path('availability/', views.classroom_availability, name='classroom_availability'),
    path('utilization/', views.classroom_utilization, name='classroom_utilization'),
]
