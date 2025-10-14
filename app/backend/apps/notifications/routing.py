"""
WebSocket路由配置
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 个人通知WebSocket
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # 系统通知WebSocket
    re_path(r'ws/system-notifications/$', consumers.SystemNotificationConsumer.as_asgi()),
    
    # 课程通知WebSocket
    re_path(r'ws/course-notifications/(?P<course_id>\d+)/$', consumers.CourseNotificationConsumer.as_asgi()),
]
