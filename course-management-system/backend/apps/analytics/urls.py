from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')
router.register(r'courses', views.CourseAnalyticsViewSet, basename='course-analytics')
router.register(r'users', views.UserAnalyticsViewSet, basename='user-analytics')
router.register(r'classrooms', views.ClassroomAnalyticsViewSet, basename='classroom-analytics')
router.register(r'enrollments', views.EnrollmentAnalyticsViewSet, basename='enrollment-analytics')

urlpatterns = [
    # 包含路由器生成的URL
    path('', include(router.urls)),
    
    # 自定义分析API端点
    path('overview/', views.OverviewAnalyticsView.as_view(), name='overview-analytics'),
    path('trends/', views.TrendAnalyticsView.as_view(), name='trend-analytics'),
    path('reports/', views.ReportAnalyticsView.as_view(), name='report-analytics'),
    
    # 实时统计API
    path('realtime/stats/', views.RealtimeStatsView.as_view(), name='realtime-stats'),
    path('realtime/activities/', views.RealtimeActivitiesView.as_view(), name='realtime-activities'),

    # 高级分析API
    path('advanced/', views.AdvancedAnalyticsView.as_view(), name='advanced-analytics'),
    
    # 导出功能
    path('export/dashboard/', views.ExportDashboardView.as_view(), name='export-dashboard'),
    path('export/courses/', views.ExportCourseAnalyticsView.as_view(), name='export-courses'),
    path('export/users/', views.ExportUserAnalyticsView.as_view(), name='export-users'),
]
