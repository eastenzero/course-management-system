#!/usr/bin/env python
"""
中等规模数据导入脚本 (179MB)
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course

User = get_user_model()

def import_medium_data():
    """导入中等规模数据"""
    print("🚀 中等规模数据导入开始")
    print("=" * 50)
    
    data_file = '/app/course_data_medium.json'
    file_size = os.path.getsize(data_file) / (1024 * 1024)  # MB
    print(f"📁 数据文件大小: {file_size:.2f} MB")
    
    # 清理现有数据
    print("🧹 清理现有数据...")
    User.objects.filter(user_type__in=['student', 'teacher']).delete()
    Course.objects.all().delete()
    
    start_time = time.time()
    
    try:
        print("📂 加载JSON数据...")
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        load_time = time.time() - start_time
        print(f"✅ JSON加载完成，耗时 {load_time:.1f} 秒")
        
        # 统计数据
        students_count = len(data.get('students', []))
        teachers_count = len(data.get('teachers', []))
        courses_count = len(data.get('courses', []))
        
        print(f"\n📊 数据统计:")
        print(f"   学生: {students_count:,}")
        print(f"   教师: {teachers_count:,}")
        print(f"   课程: {courses_count:,}")
        
        # 导入学生
        if students_count > 0:
            import_students(data['students'])
        
        # 导入教师
        if teachers_count > 0:
            import_teachers(data['teachers'])
        
        # 导入课程
        if courses_count > 0:
            import_courses(data['courses'])
        
        total_time = time.time() - start_time
        print(f"\n🎉 导入完成，总耗时 {total_time:.1f} 秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def import_students(students_data, batch_size=1000):
    """导入学生数据"""
    print(f"\n👥 开始导入 {len(students_data):,} 名学生...")
    
    password_hash = make_password('student123')
    imported_count = 0
    
    for i in range(0, len(students_data), batch_size):
        batch = students_data[i:i + batch_size]
        
        try:
            with transaction.atomic():
                users_to_create = []
                profiles_to_create = []
                
                for student in batch:
                    username = f"student_{student.get('student_id', f'auto_{i}')}"
                    
                    if not User.objects.filter(username=username).exists():
                        user = User(
                            username=username,
                            email=f"{username}@university.edu.cn",
                            first_name=student.get('name', 'Student').split()[0],
                            last_name=student.get('name', '').split()[-1] if len(student.get('name', '').split()) > 1 else '',
                            user_type='student',
                            department=student.get('department', '未分配'),
                            password=password_hash,
                            student_id=str(student.get('student_id', ''))
                        )
                        users_to_create.append(user)
                
                # 批量创建用户
                if users_to_create:
                    created_users = User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    imported_count += len(users_to_create)
                    
                print(f"   📈 已导入 {imported_count:,} 名学生...")
                
        except Exception as e:
            print(f"   ⚠️ 学生批次导入错误: {e}")
            continue
    
    print(f"✅ 学生导入完成: {imported_count:,}")
    return imported_count

def import_teachers(teachers_data, batch_size=1000):
    """导入教师数据"""
    print(f"\n👨‍🏫 开始导入 {len(teachers_data):,} 名教师...")
    
    password_hash = make_password('teacher123')
    imported_count = 0
    
    for i in range(0, len(teachers_data), batch_size):
        batch = teachers_data[i:i + batch_size]
        
        try:
            with transaction.atomic():
                users_to_create = []
                
                for teacher in batch:
                    username = f"teacher_{teacher.get('employee_id', f'auto_{i}')}"
                    
                    if not User.objects.filter(username=username).exists():
                        user = User(
                            username=username,
                            email=f"{username}@university.edu.cn",
                            first_name=teacher.get('name', 'Teacher').split()[0],
                            last_name=teacher.get('name', '').split()[-1] if len(teacher.get('name', '').split()) > 1 else '',
                            user_type='teacher',
                            department=teacher.get('department', '未分配'),
                            password=password_hash,
                            employee_id=str(teacher.get('employee_id', ''))
                        )
                        users_to_create.append(user)
                
                if users_to_create:
                    User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                    imported_count += len(users_to_create)
                    
                print(f"   📈 已导入 {imported_count:,} 名教师...")
                
        except Exception as e:
            print(f"   ⚠️ 教师批次导入错误: {e}")
            continue
    
    print(f"✅ 教师导入完成: {imported_count:,}")
    return imported_count

def import_courses(courses_data, batch_size=1000):
    """导入课程数据"""
    print(f"\n📚 开始导入 {len(courses_data):,} 门课程...")
    
    imported_count = 0
    
    for i in range(0, len(courses_data), batch_size):
        batch = courses_data[i:i + batch_size]
        
        try:
            with transaction.atomic():
                courses_to_create = []
                
                for course in batch:
                    if not Course.objects.filter(course_id=course.get('course_id')).exists():
                        course_obj = Course(
                            course_id=course.get('course_id'),
                            name=course.get('name', '未命名课程'),
                            description=course.get('description', ''),
                            credits=course.get('credits', 3),
                            department=course.get('department', '未分配'),
                            semester=course.get('semester', '2024-1'),
                            capacity=course.get('capacity', 50)
                        )
                        courses_to_create.append(course_obj)
                
                if courses_to_create:
                    Course.objects.bulk_create(courses_to_create, ignore_conflicts=True)
                    imported_count += len(courses_to_create)
                    
                print(f"   📈 已导入 {imported_count:,} 门课程...")
                
        except Exception as e:
            print(f"   ⚠️ 课程批次导入错误: {e}")
            continue
    
    print(f"✅ 课程导入完成: {imported_count:,}")
    return imported_count

def main():
    """主函数"""
    success = import_medium_data()
    
    if success:
        # 统计最终结果
        total_users = User.objects.count()
        students = User.objects.filter(user_type='student').count()
        teachers = User.objects.filter(user_type='teacher').count()
        courses = Course.objects.count()
        
        print(f"\n📊 最终统计:")
        print(f"   总用户: {total_users:,}")
        print(f"   学生: {students:,}")
        print(f"   教师: {teachers:,}")
        print(f"   课程: {courses:,}")
        print("=" * 50)

if __name__ == '__main__':
    main()