#!/usr/bin/env python
"""
监控百万级数据导入进度
"""
import os
import sys
import django
import time
from datetime import datetime

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()

def check_import_progress():
    """检查导入进度"""
    print(f"\n📊 数据导入进度监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 统计用户数量
    total_users = User.objects.count()
    student_users = User.objects.filter(user_type='student').count()
    teacher_users = User.objects.filter(user_type='teacher').count()
    admin_users = User.objects.filter(user_type='admin').count()
    
    print(f"👥 用户统计:")
    print(f"   总用户数: {total_users:,}")
    print(f"   学生用户: {student_users:,}")
    print(f"   教师用户: {teacher_users:,}")
    print(f"   管理员用户: {admin_users:,}")
    
    # 统计档案数量
    student_profiles = StudentProfile.objects.count()
    teacher_profiles = TeacherProfile.objects.count()
    
    print(f"\n📋 档案统计:")
    print(f"   学生档案: {student_profiles:,}")
    print(f"   教师档案: {teacher_profiles:,}")
    
    # 统计课程数量
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    print(f"\n📚 课程统计:")
    print(f"   课程总数: {total_courses:,}")
    print(f"   选课记录: {total_enrollments:,}")
    
    # 计算完成度（基于百万级目标）
    expected_students = 100000
    expected_teachers = 5000
    expected_courses = 12000
    
    student_progress = (student_users / expected_students) * 100
    teacher_progress = (teacher_users / expected_teachers) * 100
    course_progress = (total_courses / expected_courses) * 100
    
    print(f"\n📈 导入进度:")
    print(f"   学生导入进度: {student_progress:.1f}% ({student_users:,}/{expected_students:,})")
    print(f"   教师导入进度: {teacher_progress:.1f}% ({teacher_users:,}/{expected_teachers:,})")
    print(f"   课程导入进度: {course_progress:.1f}% ({total_courses:,}/{expected_courses:,})")
    
    print("=" * 60)

if __name__ == '__main__':
    check_import_progress()