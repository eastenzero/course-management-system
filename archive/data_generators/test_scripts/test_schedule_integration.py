#!/usr/bin/env python3
"""
测试课程表与选课系统集成的脚本
验证数据流的正确性
"""

import os
import sys
import django
from django.conf import settings

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    exit(1)

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from apps.students.services import StudentService
from apps.teachers.services import TeacherService

User = get_user_model()

def test_data_flow():
    """测试课程表数据流"""
    print("=" * 50)
    print("测试课程表与选课系统数据流集成")
    print("=" * 50)
    
    # 1. 检查基础数据
    print("\n1. 检查基础数据...")
    users_count = User.objects.count()
    courses_count = Course.objects.count()
    enrollments_count = Enrollment.objects.count()
    schedules_count = Schedule.objects.count()
    time_slots_count = TimeSlot.objects.count()
    
    print(f"   用户数量: {users_count}")
    print(f"   课程数量: {courses_count}")
    print(f"   选课记录数量: {enrollments_count}")
    print(f"   排课记录数量: {schedules_count}")
    print(f"   时间段数量: {time_slots_count}")
    
    if not all([users_count, courses_count, schedules_count, time_slots_count]):
        print("   ❌ 基础数据不完整")
        return False
    
    # 2. 测试学生课程表服务
    print("\n2. 测试学生课程表服务...")
    students = User.objects.filter(user_type='student')[:3]
    
    if not students:
        print("   ❌ 没有学生用户")
        return False
    
    for student in students:
        print(f"   测试学生: {student.username}")
        
        # 检查选课记录
        enrollments = Enrollment.objects.filter(
            student=student,
            status='enrolled',
            is_active=True
        ).count()
        print(f"     选课数量: {enrollments}")
        
        # 测试课程表获取
        try:
            service = StudentService(student)
            schedule_data = service.get_course_schedule()
            print(f"     课程表条目: {len(schedule_data)}")
            
            # 验证数据结构
            if schedule_data:
                first_item = schedule_data[0]
                required_fields = [
                    'course_id', 'course_name', 'teacher_name',
                    'classroom', 'time_slot', 'day_of_week',
                    'start_time', 'end_time'
                ]
                
                missing_fields = [field for field in required_fields if field not in first_item]
                if missing_fields:
                    print(f"     ❌ 缺少字段: {missing_fields}")
                else:
                    print("     ✅ 数据结构正确")
                    
                    # 验证不再是占位符数据
                    if first_item.get('classroom') != '待安排':
                        print("     ✅ 已关联真实排课数据")
                    else:
                        print("     ❌ 仍为占位符数据")
            
        except Exception as e:
            print(f"     ❌ 获取课程表失败: {str(e)}")
    
    # 3. 测试教师课程表服务
    print("\n3. 测试教师课程表服务...")
    teachers = User.objects.filter(user_type='teacher')[:2]
    
    if not teachers:
        print("   ❌ 没有教师用户")
        return False
    
    for teacher in teachers:
        print(f"   测试教师: {teacher.username}")
        
        # 检查授课记录
        teaching_schedules = Schedule.objects.filter(
            teacher=teacher,
            status='active'
        ).count()
        print(f"     授课安排数量: {teaching_schedules}")
        
        try:
            service = TeacherService(teacher)
            schedule_data = service.get_teaching_schedule()
            print(f"     教学安排条目: {len(schedule_data)}")
            
            if schedule_data:
                first_item = schedule_data[0]
                if first_item.get('classroom') != '待安排':
                    print("     ✅ 已关联真实排课数据")
                else:
                    print("     ❌ 仍为占位符数据")
                    
        except Exception as e:
            print(f"     ❌ 获取教学安排失败: {str(e)}")
    
    # 4. 测试时间段获取
    print("\n4. 测试时间段API...")
    try:
        time_slots = TimeSlot.objects.filter(is_active=True).order_by('order')
        print(f"   活跃时间段数量: {time_slots.count()}")
        
        if time_slots:
            for slot in time_slots[:3]:
                print(f"     {slot.name}: {slot.start_time}-{slot.end_time}")
            print("   ✅ 时间段数据正常")
        else:
            print("   ❌ 没有时间段数据")
            
    except Exception as e:
        print(f"   ❌ 获取时间段失败: {str(e)}")
    
    # 5. 测试数据关联性
    print("\n5. 测试数据关联性...")
    
    # 检查选课记录是否有对应的排课安排
    active_enrollments = Enrollment.objects.filter(
        status='enrolled',
        is_active=True
    )[:5]
    
    connected_count = 0
    total_checked = 0
    
    for enrollment in active_enrollments:
        total_checked += 1
        schedules = Schedule.objects.filter(
            course=enrollment.course,
            status='active'
        )
        
        if schedules.exists():
            connected_count += 1
            print(f"   ✅ 课程 {enrollment.course.name} 有排课安排")
        else:
            print(f"   ⚠️  课程 {enrollment.course.name} 无排课安排")
    
    connection_rate = (connected_count / total_checked * 100) if total_checked > 0 else 0
    print(f"\n   数据关联率: {connection_rate:.1f}% ({connected_count}/{total_checked})")
    
    # 总结
    print("\n" + "=" * 50)
    print("测试完成!")
    
    if connection_rate >= 50 and schedules_count > 0:
        print("✅ 课程表与选课系统集成正常")
        return True
    else:
        print("❌ 课程表与选课系统集成需要改进")
        return False

def test_api_endpoints():
    """测试API端点可访问性"""
    print("\n" + "=" * 50)
    print("API端点测试")
    print("=" * 50)
    
    endpoints = [
        '/api/v1/schedules/timeslots/simple/',
        '/api/v1/students/schedule/',
        '/api/v1/students/schedule/export/',
        '/api/v1/schedules/table/',
    ]
    
    for endpoint in endpoints:
        print(f"API端点: {endpoint}")
        # 这里实际应该使用Django Test Client，简化处理
        print("   📝 需要实际HTTP测试")

if __name__ == '__main__':
    success = test_data_flow()
    test_api_endpoints()
    
    if success:
        print("\n🎉 集成测试通过!")
        exit(0)
    else:
        print("\n❌ 集成测试失败!")
        exit(1)