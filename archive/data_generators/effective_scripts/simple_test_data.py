#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from apps.users.models import User
from apps.courses.models import Course

print('开始创建简单测试数据...')

# 创建几个教师
for i in range(1, 4):
    teacher, created = User.objects.get_or_create(
        username=f'teacher{i:02d}',
        defaults={
            'first_name': f'教师{i}',
            'email': f'teacher{i}@university.edu',
            'user_type': 'teacher',
            'department': '计算机学院',
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        print(f'创建教师: {teacher.username}')

# 创建几个学生
for i in range(1, 11):
    student, created = User.objects.get_or_create(
        username=f'student{i:03d}',
        defaults={
            'first_name': f'学生{i}',
            'email': f'student{i}@university.edu',
            'user_type': 'student',
            'student_id': f'2024{i:04d}',
            'department': '计算机学院',
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print(f'创建学生: {student.username}')

# 创建几门课程
courses_data = [
    ('Python程序设计', 'CS101'),
    ('数据结构', 'CS102'),
    ('数据库原理', 'CS201'),
]

for name, code in courses_data:
    course, created = Course.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'credits': 3,
            'hours': 48,
            'department': '计算机学院',
            'semester': '2024-2025-1',
            'academic_year': '2024-2025',
            'max_students': 50,
        }
    )
    if created:
        print(f'创建课程: {course.name}')

print('基础测试数据创建完成!')
print(f'教师数量: {User.objects.filter(user_type="teacher").count()}')
print(f'学生数量: {User.objects.filter(user_type="student").count()}')
print(f'课程数量: {Course.objects.count()}')
print()
print('测试账户:')
print('管理员: admin / admin123')
print('教师: teacher01-teacher03 / teacher123')
print('学生: student001-student010 / student123')
