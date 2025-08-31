#!/usr/bin/env python3
"""
创建测试用户脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings.production_new')
django.setup()

from django.contrib.auth import get_user_model
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile

User = get_user_model()

def create_test_users():
    """创建测试用户"""
    print("🚀 开始创建测试用户...")
    
    # 创建管理员用户
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='管理员',
            last_name='系统',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ 创建管理员用户: {admin_user.username}")
    
    # 创建教务管理员
    if not User.objects.filter(username='academic_admin').exists():
        academic_user = User.objects.create_user(
            username='academic_admin',
            email='academic@example.com',
            password='academic123',
            first_name='教务',
            last_name='管理员',
            user_type='academic_admin',
            is_staff=True
        )
        print(f"✅ 创建教务管理员: {academic_user.username}")
    
    # 创建测试教师
    if not User.objects.filter(username='teacher001').exists():
        teacher_user = User.objects.create_user(
            username='teacher001',
            email='teacher001@example.com',
            password='password123',
            first_name='张',
            last_name='教授',
            user_type='teacher'
        )
        
        # 创建教师档案
        TeacherProfile.objects.create(
            user=teacher_user,
            title='教授',
            research_area='计算机科学',
            office_location='A301',
            office_phone='13800138001',
            office_hours='周一至周五 9:00-17:00'
        )
        print(f"✅ 创建教师用户: {teacher_user.username}")
    
    # 创建测试学生
    if not User.objects.filter(username='student001').exists():
        student_user = User.objects.create_user(
            username='student001',
            email='student001@example.com',
            password='password123',
            first_name='李',
            last_name='同学',
            user_type='student'
        )
        
        # 创建学生档案
        StudentProfile.objects.create(
            user=student_user,
            admission_year=2024,
            major='计算机科学与技术',
            class_name='计科2024-1班',
            gpa=3.5,
            emergency_contact='李父',
            emergency_phone='13900139001'
        )
        print(f"✅ 创建学生用户: {student_user.username}")
    
    # 创建更多测试账号（基于之前生成的数据）
    test_accounts = [
        {'username': 'student030520', 'password': 'password123', 'type': 'student', 'name': '陈静勇'},
        {'username': 'student022199', 'password': 'password123', 'type': 'student', 'name': '何娟秀英'},
        {'username': 'teacher000453', 'password': 'password123', 'type': 'teacher', 'name': '马洋磊'},
    ]
    
    for account in test_accounts:
        if not User.objects.filter(username=account['username']).exists():
            user = User.objects.create_user(
                username=account['username'],
                email=f"{account['username']}@example.com",
                password=account['password'],
                first_name=account['name'].split()[0] if account['name'] else '',
                last_name=account['name'][1:] if len(account['name']) > 1 else '',
                user_type=account['type']
            )
            print(f"✅ 创建用户: {user.username} ({account['name']})")
    
    print(f"\n📊 总用户数: {User.objects.count()}")
    print("🎉 测试用户创建完成！")

if __name__ == "__main__":
    create_test_users()