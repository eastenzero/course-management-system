"""
ASGI config for course_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings.base')

# 初始化Django
django.setup()

# 导入Channels相关模块
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# 先获取Django ASGI应用
django_asgi_app = get_asgi_application()

# 导入WebSocket路由（稍后创建）
try:
    from apps.notifications.routing import websocket_urlpatterns
except ImportError:
    websocket_urlpatterns = []

# ASGI应用配置
application = ProtocolTypeRouter({
    # HTTP协议使用Django的ASGI应用
    "http": django_asgi_app,

    # WebSocket协议使用Channels路由
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
