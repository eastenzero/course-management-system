from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from apps.classrooms.models import Classroom
from apps.students.services import StudentService
import random

User = get_user_model()

# 为测试学生的选课创建Schedule
test_student = User.objects.filter(user_type='student').first()
print(f'为学生 {test_student.username} 创建Schedule...')

enrollments = Enrollment.objects.filter(
    student=test_student,
    status='enrolled',
    is_active=True
).select_related('course')[:2]

created_count = 0
for enrollment in enrollments:
    course = enrollment.course
    if not Schedule.objects.filter(course=course).exists():
        # 选择合适的教室
        classroom = Classroom.objects.filter(capacity__gte=50).first()
        if not classroom:
            classroom = Classroom.objects.first()
            
        # 选择教师和时间段
        teacher = course.teachers.first() or User.objects.filter(user_type='teacher').first()
        time_slot = TimeSlot.objects.filter(is_active=True).first()
        
        if teacher and classroom and time_slot:
            try:
                Schedule.objects.create(
                    course=course,
                    teacher=teacher,
                    classroom=classroom,
                    time_slot=time_slot,
                    day_of_week=1,  # 周一
                    week_range='1-18周',
                    semester='2024-2025-1',
                    academic_year='2024-2025',
                    status='active'
                )
                created_count += 1
                print(f'创建Schedule: {course.name} -> {classroom.name}')
            except Exception as e:
                print(f'创建失败: {course.name} - {e}')

print(f'创建了 {created_count} 条Schedule')

# 测试StudentService
print('\n测试StudentService:')
service = StudentService(test_student)
schedule_data = service.get_course_schedule()

print(f'获取到 {len(schedule_data)} 条记录')
if schedule_data:
    item = schedule_data[0]
    print(f'第一条记录:')
    print(f'  课程: {item["course_name"]}')
    print(f'  教室: {item["classroom"]}')
    print(f'  时间: {item["time_slot"]}')
    
    if item['classroom'] != '待安排':
        print('✅ 课程表数据修复成功!')
    else:
        print('❌ 仍为占位符数据')
else:
    print('❌ 无数据')