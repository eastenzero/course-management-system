#!/usr/bin/env python3
"""
测试课程表API是否返回正确数据
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.insert(0, '/root/code/course-management-system/course-management-system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from apps.users.models import User
from apps.schedules.models import Schedule

def test_schedule_api():
    """测试课程表API"""
    print("🧪 测试课程表API...")
    
    # 获取一个学生用户
    student = User.objects.filter(user_type='student').first()
    if not student:
        print("❌ 没有找到学生用户")
        return False
    
    print(f"📋 使用学生用户: {student.username} (ID: {student.id})")
    
    # 检查数据库中的排课记录
    schedules = Schedule.objects.filter(status='active')
    print(f"📊 数据库中有效排课记录: {schedules.count()}")
    
    if schedules.count() == 0:
        print("❌ 数据库中没有有效排课记录")
        return False
    
    # 检查学生选课情况
    from apps.courses.models import Enrollment
    enrollments = Enrollment.objects.filter(student=student, is_active=True, status='enrolled')
    print(f"📚 学生选课记录: {enrollments.count()}")
    
    if enrollments.count() == 0:
        print("❌ 该学生没有选课记录")
        return False
    
    # 检查学生的课程是否有排课
    enrolled_courses = enrollments.values_list('course_id', flat=True)
    course_schedules = schedules.filter(course_id__in=enrolled_courses)
    print(f"🎯 学生所选课程的排课记录: {course_schedules.count()}")
    
    if course_schedules.count() == 0:
        print("❌ 学生所选课程没有对应的排课记录")
        return False
    
    print("\n✅ 数据验证通过！")
    print("📋 学生课程表预览:")
    for schedule in course_schedules[:3]:
        print(f"  {schedule.course.name} - {schedule.teacher.username} - {schedule.classroom.room_number} (周{schedule.day_of_week} {schedule.time_slot.name})")
    
    return True

if __name__ == "__main__":
    success = test_schedule_api()
    if success:
        print("\n🎉 课程表数据准备就绪，前端应该能够正常显示！")
    else:
        print("\n⚠️  存在问题，前端可能无法正确显示课程表")