@echo off
echo === 课程表与选课系统集成测试 ===
echo.

echo 1. 检查Docker服务状态...
docker ps | findstr course_management_backend
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker后端服务未运行
    echo 请先运行: docker-compose up -d
    exit /b 1
)

echo ✅ Docker后端服务运行正常
echo.

echo 2. 测试数据库连接和基础数据...
docker exec course_management_backend python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot

User = get_user_model()

print('=== 数据库状态 ===')
print(f'用户数量: {User.objects.count()}')
print(f'课程数量: {Course.objects.count()}')
print(f'选课记录数量: {Enrollment.objects.count()}')
print(f'排课记录数量: {Schedule.objects.count()}')
print(f'时间段数量: {TimeSlot.objects.count()}')

# 检查数据关联性
enrollments_with_schedules = 0
total_enrollments = Enrollment.objects.filter(status='enrolled', is_active=True).count()

for enrollment in Enrollment.objects.filter(status='enrolled', is_active=True)[:10]:
    if Schedule.objects.filter(course=enrollment.course, status='active').exists():
        enrollments_with_schedules += 1

if total_enrollments > 0:
    connection_rate = (enrollments_with_schedules / min(10, total_enrollments)) * 100
    print(f'数据关联率: {connection_rate:.1f}%%')
    
    if connection_rate >= 50:
        print('✅ 课程表与选课系统关联正常')
    else:
        print('❌ 课程表与选课系统关联不足')
"

echo.
echo 3. 测试学生课程表API...
docker exec course_management_backend python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.students.services import StudentService

User = get_user_model()
student = User.objects.filter(user_type='student').first()

if student:
    print(f'测试学生: {student.username}')
    service = StudentService(student)
    
    try:
        schedule_data = service.get_course_schedule()
        print(f'获取到 {len(schedule_data)} 条课程表记录')
        
        if schedule_data:
            item = schedule_data[0]
            print(f'示例记录:')
            print(f'  课程: {item.get(\"course_name\")}')
            print(f'  教室: {item.get(\"classroom\")}')
            print(f'  时间: {item.get(\"time_slot\")}')
            
            if item.get('classroom') and item.get('classroom') != '待安排':
                print('✅ 课程表数据已修复，不再是占位符')
            else:
                print('❌ 课程表仍返回占位符数据')
        else:
            print('⚠️  该学生暂无课程安排')
            
    except Exception as e:
        print(f'❌ 获取课程表失败: {e}')
else:
    print('❌ 未找到学生用户')
"

echo.
echo 4. 测试时间段API...
docker exec course_management_backend python manage.py shell -c "
from apps.schedules.models import TimeSlot

time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
print(f'活跃时间段数量: {time_slots.count()}')

for slot in time_slots[:3]:
    print(f'  {slot.name}: {slot.start_time} - {slot.end_time}')

if time_slots.count() > 0:
    print('✅ 时间段配置正常')
else:
    print('❌ 缺少时间段配置')
"

echo.
echo === 测试完成 ===