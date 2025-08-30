# file: backend/apps/algorithms/urls.py
# 功能: 算法API URL配置

from django.urls import path
from . import views

app_name = 'algorithms'

urlpatterns = [
    # 排课生成
    path('generate/', views.generate_schedule, name='generate_schedule'),
    
    # 排课分析
    path('analyze/', views.analyze_schedule, name='analyze_schedule'),
    
    # 排课优化
    path('optimize/', views.optimize_schedule, name='optimize_schedule'),
    
    # 统计信息
    path('statistics/', views.get_algorithm_statistics, name='get_statistics'),
    
    # 导出排课
    path('export/', views.export_schedule, name='export_schedule'),
    
    # 冲突解决
    # path('resolve-conflicts/', views.resolve_conflicts, name='resolve_conflicts'),
    
    # 算法配置
    # path('config/', views.get_algorithm_config, name='get_config'),
    # path('config/update/', views.update_algorithm_config, name='update_config'),
    
    # 教师偏好管理
    # path('preferences/', views.manage_teacher_preferences, name='manage_preferences'),
    
    # 课程需求管理
    # path('requirements/', views.manage_course_requirements, name='manage_requirements'),
]
