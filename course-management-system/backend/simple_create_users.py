#!/usr/bin/env python3
"""
简化版创建测试用户脚本 - 使用简单settings配置
"""

import os
import sys
import django

# 设置Django环境 - 使用简单的settings配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_simple_test_users():
    """创建简化版测试用户"""
    print("🚀 开始创建简化版测试用户...")
    
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
    
    # 创建测试教师
    if not User.objects.filter(username='teacher001').exists():
        teacher_user = User.objects.create_user(
            username='teacher001',
            email='teacher001@example.com',
            password='password123',
            first_name='张',
            last_name='教授',
            user_type='teacher',
            employee_id='T001'
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
            user_type='student',
            student_id='S001'
        )
        print(f"✅ 创建学生用户: {student_user.username}")
    
    # 创建更多测试用户
    test_users = [
        {'username': 'teacher002', 'type': 'teacher', 'name': '王教授', 'employee_id': 'T002'},
        {'username': 'student002', 'type': 'student', 'name': '陈同学', 'student_id': 'S002'},
        {'username': 'student003', 'type': 'student', 'name': '刘同学', 'student_id': 'S003'},
    ]
    
    for user_data in test_users:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                email=f"{user_data['username']}@example.com",
                password='password123',
                first_name=user_data['name'][0],
                last_name=user_data['name'][1:],
                user_type=user_data['type']
            )
            
            # 设置工号或学号
            if user_data['type'] == 'teacher':
                user.employee_id = user_data['employee_id']
            else:
                user.student_id = user_data['student_id']
            user.save()
            
            print(f"✅ 创建用户: {user.username} ({user_data['name']})")
    
    print(f"\n📊 总用户数: {User.objects.count()}")
    print("🎉 简化版测试用户创建完成！")
    print("\n测试账号信息:")
    print("管理员账号: admin / admin123")
    print("教师账号: teacher001 / password123")
    print("学生账号: student001 / password123")

if __name__ == "__main__":
    create_simple_test_users()