from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = '通知系统'

    def ready(self):
        # 导入信号处理器
        try:
            import apps.notifications.signals
        except ImportError:
            pass
