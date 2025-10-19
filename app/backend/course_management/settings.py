"""
Minimal Django settings for testing
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'course_management',
    'apps.users.apps.UsersConfig',
    'apps.courses.apps.CoursesConfig',
    'apps.schedules.apps.SchedulesConfig',
    'apps.classrooms.apps.ClassroomsConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.students.apps.StudentsConfig',
    'apps.teachers.apps.TeachersConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.files.apps.FilesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'course_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'course_management.wsgi.application'

# Database
USE_SQLITE = os.environ.get('USE_SQLITE', '0') in ['1', 'true', 'True']
if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'course_management'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres123'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/app/static')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'course_management_cache',
        'TIMEOUT': 300,
    },
    'api_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api_cache',
        'TIMEOUT': 300,
    }
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

SCHEDULE_CONFIG = {
    'TERM_WEEKS': int(os.environ.get('TERM_WEEKS', 18)),
    'SESSION_DURATION_HOURS': float(os.environ.get('SESSION_DURATION_HOURS', 2)),
    'sessions_per_week_cap': int(os.environ.get('SCHEDULE_SESSIONS_PER_WEEK_CAP', 2)),
    'teacher_same_day_penalty': float(os.environ.get('SCHEDULE_TEACHER_SAME_DAY_PENALTY', 8)),
    'time_slot_usage_penalty': float(os.environ.get('SCHEDULE_TIME_SLOT_USAGE_PENALTY', 2.0)),
    'teacher_day_load_limit': int(os.environ.get('SCHEDULE_TEACHER_DAY_LOAD_LIMIT', 3)),
    'avoid_noon_default': os.environ.get('SCHEDULE_AVOID_NOON_DEFAULT', '0') in ['1', 'true', 'True'],
    'preferred_classroom_bonus': float(os.environ.get('SCHEDULE_PREFERRED_CLASSROOM_BONUS', 20)),
    'preferred_time_slot_bonus': float(os.environ.get('SCHEDULE_PREFERRED_TIME_SLOT_BONUS', 15)),
    'preferred_day_bonus': float(os.environ.get('SCHEDULE_PREFERRED_DAY_BONUS', 10)),
    'priority_weight': float(os.environ.get('SCHEDULE_PRIORITY_WEIGHT', 10)),
    'noon_penalty': float(os.environ.get('SCHEDULE_NOON_PENALTY', 30)),
    'good_time_slot_order_min': int(os.environ.get('SCHEDULE_GOOD_TS_ORDER_MIN', 2)),
    'good_time_slot_order_max': int(os.environ.get('SCHEDULE_GOOD_TS_ORDER_MAX', 6)),
    'good_time_slot_bonus': float(os.environ.get('SCHEDULE_GOOD_TS_BONUS', 5)),
    'two_hour_minutes_min': int(os.environ.get('SCHEDULE_TWO_HOUR_MIN', 115)),
    'two_hour_minutes_max': int(os.environ.get('SCHEDULE_TWO_HOUR_MAX', 125)),
    'max_daily_sessions_per_course': int(os.environ.get('SCHEDULE_MAX_DAILY_SESSIONS_PER_COURSE', 1)),
}
