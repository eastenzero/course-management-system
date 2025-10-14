#!/bin/bash

# 仪表板数据设置脚本
echo "=== 设置仪表板数据 ==="

# 1. 初始化数据库
echo "1. 初始化数据库..."
bash scripts/init_database.sh

# 2. 创建示例数据
echo "2. 创建示例数据..."
sudo docker-compose exec backend python -c "
import sys
sys.path.append('/app')
exec(open('/app/scripts/create_sample_data.py').read())
"

# 3. 验证数据
echo "3. 验证数据..."
sudo docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from apps.notifications.models import Notification

User = get_user_model()

print('=== 数据验证结果 ===')
print(f'用户总数: {User.objects.count()}')
print(f'学生数: {User.objects.filter(user_type=\"student\").count()}')
print(f'教师数: {User.objects.filter(user_type=\"teacher\").count()}')
print(f'课程数: {Course.objects.count()}')
print(f'选课记录数: {Enrollment.objects.count()}')
print(f'排课记录数: {Schedule.objects.count()}')
print(f'时间段数: {TimeSlot.objects.count()}')
print(f'通知数: {Notification.objects.count()}')

# 测试仪表板数据
student = User.objects.filter(user_type='student').first()
if student:
    from apps.students.services import StudentService
    service = StudentService(student)
    dashboard_data = service.get_dashboard_data()
    print(f'学生今日课程数: {len(dashboard_data[\"today_schedule\"])}')
    print(f'学生通知数: {len(dashboard_data[\"notifications\"])}')
    print(f'学生截止日期数: {len(dashboard_data[\"upcoming_deadlines\"])}')

teacher = User.objects.filter(user_type='teacher').first()
if teacher:
    from apps.teachers.services import TeacherService
    service = TeacherService(teacher)
    dashboard_data = service.get_dashboard_data()
    print(f'教师今日课程数: {len(dashboard_data[\"today_schedule\"])}')
    print(f'教师待处理任务数: {len(dashboard_data[\"pending_tasks\"])}')
"

echo "=== 设置完成 ==="
echo "现在可以使用以下账号登录："
echo "学生账号: student001 / password123"
echo "教师账号: teacher001 / password123"
echo "管理员账号: admin / admin123"
