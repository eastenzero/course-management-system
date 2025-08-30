#!/bin/bash

# 数据库初始化脚本
echo "=== 开始初始化数据库 ==="

# 1. 运行数据库迁移
echo "1. 运行数据库迁移..."
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate

# 2. 创建超级用户（如果不存在）
echo "2. 创建超级用户..."
sudo docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', user_type='admin')
    print('超级用户 admin 创建成功')
else:
    print('超级用户 admin 已存在')
"

# 3. 创建基础时间段数据
echo "3. 创建基础时间段数据..."
sudo docker-compose exec backend python manage.py shell -c "
from apps.schedules.models import TimeSlot
from datetime import time

time_slots = [
    {'name': '第1节', 'start_time': time(8, 0), 'end_time': time(8, 45), 'order': 1},
    {'name': '第2节', 'start_time': time(8, 55), 'end_time': time(9, 40), 'order': 2},
    {'name': '第3节', 'start_time': time(10, 0), 'end_time': time(10, 45), 'order': 3},
    {'name': '第4节', 'start_time': time(10, 55), 'end_time': time(11, 40), 'order': 4},
    {'name': '第5节', 'start_time': time(14, 0), 'end_time': time(14, 45), 'order': 5},
    {'name': '第6节', 'start_time': time(14, 55), 'end_time': time(15, 40), 'order': 6},
    {'name': '第7节', 'start_time': time(16, 0), 'end_time': time(16, 45), 'order': 7},
    {'name': '第8节', 'start_time': time(16, 55), 'end_time': time(17, 40), 'order': 8},
]

for slot_data in time_slots:
    TimeSlot.objects.get_or_create(
        order=slot_data['order'],
        defaults=slot_data
    )
print(f'时间段数据创建完成，共 {TimeSlot.objects.count()} 个时间段')
"

echo "=== 数据库初始化完成 ==="
