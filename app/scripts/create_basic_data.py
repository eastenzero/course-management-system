#!/usr/bin/env python
"""
创建基础数据脚本（不依赖 notifications）
用于生成仪表板所需的最小数据集
"""

import os
import sys
import django
from datetime import datetime, date, timedelta

# 设置 Django 环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings.development')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.schedules.models import Schedule, TimeSlot
from apps.classrooms.models import Classroom, Building
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile

User = get_user_model()

def create_basic_data():
    """创建基础数据"""
    print("=== 开始创建基础数据 ===")
    
    # 1. 创建用户
    print("1. 创建用户...")
    
    # 创建学生（使用现有的学生用户）
    try:
        student = User.objects.get(username='student')
        print(f"使用现有学生: {student.username}")
    except User.DoesNotExist:
        student = User.objects.create_user(
            username='student001',
            email='student001@example.com',
            first_name='张',
            last_name='三',
            user_type='student',
            student_id='2024001001',
            password='password123',
            is_active=True,
        )
        print(f"创建学生: {student.username}")

    # 创建教师（使用现有的教师用户）
    try:
        teacher = User.objects.get(username='teacher')
        print(f"使用现有教师: {teacher.username}")
    except User.DoesNotExist:
        teacher = User.objects.create_user(
            username='teacher001',
            email='teacher001@example.com',
            first_name='李',
            last_name='老师',
            user_type='teacher',
            employee_id='T002',
            password='password123',
            is_active=True,
        )
        print(f"创建教师: {teacher.username}")
    
    # 2. 创建建筑和教室
    print("2. 创建教室...")
    building, _ = Building.objects.get_or_create(
        name='教学楼A',
        defaults={
            'code': 'A',
            'address': '校园中心区',
            'description': '主教学楼',
        }
    )
    
    classroom, _ = Classroom.objects.get_or_create(
        room_number='101',
        building=building,
        defaults={
            'name': 'A101',
            'floor': 1,
            'capacity': 50,
            'room_type': 'lecture',
            'is_active': True,
        }
    )
    
    # 3. 创建当前学期课程
    print("3. 创建课程...")
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # 根据月份确定学期
    if current_month >= 9 or current_month <= 1:
        semester = f"{current_year}-{current_year+1}-1"  # 秋季学期
        academic_year = f"{current_year}-{current_year+1}"
    else:
        semester = f"{current_year-1}-{current_year}-2"  # 春季学期
        academic_year = f"{current_year-1}-{current_year}"
    
    course, created = Course.objects.get_or_create(
        code='CS101',
        defaults={
            'name': '计算机科学导论',
            'english_name': 'Introduction to Computer Science',
            'credits': 3,
            'hours': 48,
            'course_type': 'required',
            'department': '计算机科学与技术学院',
            'semester': semester,
            'academic_year': academic_year,
            'description': '计算机科学基础课程',
            'max_students': 50,
            'min_students': 10,
            'is_active': True,
            'is_published': True,
        }
    )
    
    # 关联教师
    course.teachers.add(teacher)
    print(f"创建课程: {course.name} ({semester})")
    
    # 4. 创建选课记录
    print("4. 创建选课记录...")
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            'status': 'enrolled',
            'is_active': True,
        }
    )
    if created:
        print(f"学生 {student.username} 选课 {course.name}")
    
    # 5. 创建排课记录（今天有课）
    print("5. 创建排课记录...")
    today = date.today()
    weekday = today.isoweekday()  # 1-7
    
    # 获取第一个时间段
    time_slot = TimeSlot.objects.first()
    if time_slot:
        schedule, created = Schedule.objects.get_or_create(
            course=course,
            teacher=teacher,
            classroom=classroom,
            time_slot=time_slot,
            day_of_week=weekday,
            semester=semester,
            defaults={
                'academic_year': academic_year,
                'week_range': '1-16周',
                'status': 'active',
            }
        )
        if created:
            print(f"创建排课: {course.name} - 周{['一','二','三','四','五','六','日'][weekday-1]} {time_slot.name}")
    
    # 6. 创建档案信息
    print("6. 创建档案信息...")
    student_profile, _ = StudentProfile.objects.get_or_create(
        user=student,
        defaults={
            'admission_year': 2024,
            'major': '计算机科学与技术',
            'class_name': '计科2024-1班',
            'enrollment_status': 'enrolled',
        }
    )
    
    teacher_profile, _ = TeacherProfile.objects.get_or_create(
        user=teacher,
        defaults={
            'title': 'lecturer',
            'research_area': '计算机科学教育',
            'office_location': 'A座301',
            'office_hours': '周二、周四 14:00-16:00',
        }
    )
    
    print("=== 基础数据创建完成 ===")
    print(f"学期: {semester}")
    print(f"学生账号: {student.username} / password123")
    print(f"教师账号: {teacher.username} / password123")
    print(f"课程: {course.name}")
    print(f"今日课程: 周{['一','二','三','四','五','六','日'][weekday-1]} {time_slot.name if time_slot else '无'}")
    print("现在可以登录前端查看仪表板数据了！")

if __name__ == '__main__':
    create_basic_data()
