# file: backend/apps/algorithms/apps.py
# 功能: 算法应用配置

from django.apps import AppConfig


class AlgorithmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.algorithms'
    verbose_name = '智能排课算法'
