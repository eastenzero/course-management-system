"""
排课算法API的URL配置
"""

from django.urls import path
from .views_algorithm import (
    run_scheduling_algorithm,
    apply_scheduling_results,
    get_scheduling_status,
    validate_scheduling_constraints
)

app_name = 'scheduling_algorithm'

urlpatterns = [
    # 运行排课算法
    path('api/scheduling/run-algorithm/', run_scheduling_algorithm, name='run-algorithm'),
    
    # 应用排课结果
    path('api/scheduling/apply-results/', apply_scheduling_results, name='apply-results'),
    
    # 获取排课状态
    path('api/scheduling/status/', get_scheduling_status, name='get-status'),
    
    # 验证排课约束
    path('api/scheduling/validate-constraints/', validate_scheduling_constraints, name='validate-constraints'),
]