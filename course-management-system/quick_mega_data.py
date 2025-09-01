#!/usr/bin/env python
"""
快速生成演示数据 - 简化版
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password
import random

User = get_user_model()

def generate_quick_mega_data():
    """快速生成演示数据"""
    print("🚀 快速生成百万级演示数据...")
    
    # 小规模演示数据
    STUDENT_COUNT = 1000
    TEACHER_COUNT = 50
    BATCH_SIZE = 100
    
    print(f"📊 生成 {STUDENT_COUNT} 学生和 {TEACHER_COUNT} 教师...")
    
    # 清理现有数据
    User.objects.filter(username__startswith='mega_').delete()
    
    # 生成学生
    student_password = make_password('student123')
    departments = ['计算机学院', '软件学院', '信息学院', '人工智能学院']
    
    created_students = 0
    for i in range(0, STUDENT_COUNT, BATCH_SIZE):
        batch_size = min(BATCH_SIZE, STUDENT_COUNT - i)
        users_to_create = []
        
        for j in range(batch_size):
            student_id = f"mega_student_{i+j+1:06d}"
            user = User(
                username=student_id,
                email=f"{student_id}@university.edu.cn",
                first_name=f"学生{i+j+1}",
                last_name="姓",
                user_type='student',
                department=random.choice(departments),
                student_id=student_id,
                password=student_password,
                is_active=True
            )
            users_to_create.append(user)
        
        with transaction.atomic():
            User.objects.bulk_create(users_to_create, ignore_conflicts=True)
            created_students += len(users_to_create)
            print(f"   已创建 {created_students} 学生...")
    
    # 生成教师
    teacher_password = make_password('teacher123')
    created_teachers = 0
    
    for i in range(0, TEACHER_COUNT, BATCH_SIZE):
        batch_size = min(BATCH_SIZE, TEACHER_COUNT - i)
        users_to_create = []
        
        for j in range(batch_size):
            teacher_id = f"mega_teacher_{i+j+1:04d}"
            user = User(
                username=teacher_id,
                email=f"{teacher_id}@university.edu.cn",
                first_name=f"教师{i+j+1}",
                last_name="老师",
                user_type='teacher',
                department=random.choice(departments),
                employee_id=teacher_id,
                password=teacher_password,
                is_active=True
            )
            users_to_create.append(user)
        
        with transaction.atomic():
            User.objects.bulk_create(users_to_create, ignore_conflicts=True)
            created_teachers += len(users_to_create)
            print(f"   已创建 {created_teachers} 教师...")
    
    print(f"✅ 完成！创建了 {created_students} 学生和 {created_teachers} 教师")
    
    # 验证
    total_users = User.objects.count()
    mega_users = User.objects.filter(username__startswith='mega_').count()
    print(f"🔍 验证: 总用户 {total_users}, 百万级演示用户 {mega_users}")
    
    return created_students + created_teachers

if __name__ == '__main__':
    try:
        result = generate_quick_mega_data()
        print(f"✅ 成功生成 {result} 条记录")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()