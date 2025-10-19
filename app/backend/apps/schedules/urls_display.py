"""
课程表显示相关的URL配置
"""

from django.urls import path
from .views_schedule_display import (
    schedule_display_view,
    generate_schedule_api,
    schedule_json_api
)

app_name = 'schedule_display'

urlpatterns = [
    # 课程表显示页面
    path('schedule/', schedule_display_view, name='schedule-display'),
    
    # API接口
    path('api/scheduling/generate/', generate_schedule_api, name='generate-schedule'),
    path('api/scheduling/json/', schedule_json_api, name='schedule-json'),
]