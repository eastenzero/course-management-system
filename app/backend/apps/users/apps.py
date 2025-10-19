from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'  # 这个标签用于AUTH_USER_MODEL
    verbose_name = '用户管理'
