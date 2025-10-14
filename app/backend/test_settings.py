"""
测试专用设置文件
基于simple_settings.py，但针对测试环境进行了优化
"""

from simple_settings import *

# 测试数据库配置 - 使用内存SQLite数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 禁用日志输出
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 测试时禁用迁移
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 密码验证器 - 测试时使用简单密码
AUTH_PASSWORD_VALIDATORS = []

# 邮件后端 - 测试时使用内存后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 文件存储 - 测试时使用临时目录
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# 禁用调试工具栏
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# 测试时禁用Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 测试时使用简单的密码哈希器
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 禁用静态文件收集
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 测试时禁用CSRF
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# 时区设置
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'

# 测试覆盖率设置
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

COVERAGE_MODULE_EXCLUDES += [
    'venv', 'virtualenv', '__pycache__',
    'node_modules', '.git', '.tox',
]

COVERAGE_REPORT_HTML_OUTPUT_DIR = 'htmlcov'

# 测试数据库名称
TEST_DATABASE_NAME = ':memory:'

# 测试时的安全设置
SECRET_KEY = 'test-secret-key-only-for-testing-do-not-use-in-production'
ALLOWED_HOSTS = ['*']

# 禁用一些中间件以加快测试速度
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# 测试时的REST框架设置
REST_FRAMEWORK.update({
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
})

# 禁用WebSocket相关设置
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

print("🧪 使用测试配置文件: test_settings.py")
