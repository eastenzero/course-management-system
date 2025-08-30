#!/bin/bash

# Docker启动脚本
set -e

echo "正在启动Django应用..."

# 等待数据库就绪 - 使用Django的数据库检查
echo "等待数据库连接..."
python manage.py check --database default || echo "数据库检查失败，但继续启动..."

# 运行数据库迁移
echo "跳过数据库迁移..."
# python manage.py migrate --fake-initial --verbosity=1

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo "检查超级用户..."
# python manage.py shell << END
# from django.contrib.auth import get_user_model
# User = get_user_model()
#
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser(
#         username='admin',
#         email='admin@example.com',
#         password='admin123',
#         user_type='admin'
#     )
#     print('超级用户已创建: admin / admin123')
# else:
#     print('超级用户已存在')
# END
echo "跳过超级用户创建..."

# 创建测试数据
echo "创建测试数据..."
# python create_test_data.py || echo "测试数据创建失败或已存在"
echo "跳过测试数据创建..."

echo "启动Gunicorn服务器..."
# 优化的Gunicorn配置：
# --workers 2: 减少worker数量，降低内存使用
# --timeout 300: 增加超时时间到5分钟
# --worker-class sync: 使用同步worker
# --max-requests 1000: 每个worker处理1000个请求后重启
# --max-requests-jitter 100: 添加随机抖动避免同时重启
# --preload: 预加载应用程序
# --log-level info: 增加日志级别
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 300 \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    course_management.wsgi:application
