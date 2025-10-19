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
from .views_comparison import compare_scheduling_algorithms
from .views_visualization import (
    get_schedule_table,
    get_statistics_chart,
    get_conflict_report
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
    
    # 算法性能对比
    path('api/scheduling/compare-algorithms/', compare_scheduling_algorithms, name='compare-algorithms'),
    
    # 可视化API
    path('api/scheduling/visualization/schedule-table/', get_schedule_table, name='schedule-table'),
    path('api/scheduling/visualization/statistics/', get_statistics_chart, name='statistics-chart'),
    path('api/scheduling/visualization/conflicts/', get_conflict_report, name='conflict-report'),
]