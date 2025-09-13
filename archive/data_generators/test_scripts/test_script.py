from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from apps.students.services import StudentService
from apps.teachers.services import TeacherService

User = get_user_model()

print('=' * 50)
print('课程表与选课系统集成测试')
print('=' * 50)

# 1. 数据库状态检查
print('\n1. 数据库状态检查:')
users_count = User.objects.count()
courses_count = Course.objects.count()
enrollments_count = Enrollment.objects.count()
schedules_count = Schedule.objects.count()
time_slots_count = TimeSlot.objects.count()

print(f'   用户数量: {users_count}')
print(f'   课程数量: {courses_count}')
print(f'   选课记录数量: {enrollments_count}')
print(f'   排课记录数量: {schedules_count}')
print(f'   时间段数量: {time_slots_count}')

# 2. 学生课程表服务测试
print('\n2. 学生课程表服务测试:')
students = User.objects.filter(user_type='student')[:2]

for student in students:
    print(f'   测试学生: {student.username}')
    
    # 检查选课记录
    enrollments = Enrollment.objects.filter(
        student=student,
        status='enrolled',
        is_active=True
    ).count()
    print(f'     选课数量: {enrollments}')
    
    # 测试课程表获取
    try:
        service = StudentService(student)
        schedule_data = service.get_course_schedule()
        print(f'     课程表条目: {len(schedule_data)}')
        
        if schedule_data:
            first_item = schedule_data[0]
            print(f'     第一条记录:')
            print(f'       课程: {first_item.get("course_name")}')
            print(f'       教室: {first_item.get("classroom")}')
            print(f'       时间: {first_item.get("time_slot")}')
            
            if first_item.get('classroom') and first_item.get('classroom') != '待安排':
                print('     ✅ 已关联真实排课数据')
            else:
                print('     ❌ 仍为占位符数据')
        else:
            print('     ⚠️  无课程表数据')
            
    except Exception as e:
        print(f'     ❌ 获取课程表失败: {e}')

# 3. 教师课程表服务测试
print('\n3. 教师课程表服务测试:')
teachers = User.objects.filter(user_type='teacher')[:1]

for teacher in teachers:
    print(f'   测试教师: {teacher.username}')
    
    try:
        service = TeacherService(teacher)
        schedule_data = service.get_teaching_schedule()
        print(f'     教学安排条目: {len(schedule_data)}')
        
        if schedule_data:
            first_item = schedule_data[0]
            print(f'     第一条记录:')
            print(f'       课程: {first_item.get("course_name")}')
            print(f'       教室: {first_item.get("classroom")}')
            
            if first_item.get('classroom') and first_item.get('classroom') != '待安排':
                print('     ✅ 已关联真实排课数据')
            else:
                print('     ❌ 仍为占位符数据')
                
    except Exception as e:
        print(f'     ❌ 获取教学安排失败: {e}')

# 4. 时间段配置测试
print('\n4. 时间段配置测试:')
time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
print(f'   活跃时间段数量: {time_slots.count()}')

for slot in time_slots[:3]:
    print(f'     {slot.name}: {slot.start_time} - {slot.end_time}')

if time_slots.count() > 0:
    print('   ✅ 时间段配置正常')
else:
    print('   ❌ 缺少时间段配置')

# 5. 数据关联性测试
print('\n5. 数据关联性测试:')
enrolled_courses = Enrollment.objects.filter(
    status='enrolled',
    is_active=True
).values_list('course_id', flat=True)[:10]

connected_courses = 0
for course_id in enrolled_courses:
    if Schedule.objects.filter(course_id=course_id, status='active').exists():
        connected_courses += 1

if len(enrolled_courses) > 0:
    connection_rate = (connected_courses / len(enrolled_courses)) * 100
    print(f'   数据关联率: {connection_rate:.1f}% ({connected_courses}/{len(enrolled_courses)})')
    
    if connection_rate >= 50:
        print('   ✅ 课程表与选课系统关联良好')
    else:
        print('   ⚠️  数据关联需要改进')

print('\n' + '=' * 50)
print('测试完成')
print('=' * 50)