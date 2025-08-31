#!/usr/bin/env python
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from django.db import transaction

User = get_user_model()

print("开始快速数据生成...")

with transaction.atomic():
    # 获取现有数据
    students = list(User.objects.filter(user_type='student'))
    teachers = list(User.objects.filter(user_type='teacher'))
    
    print(f"现有学生: {len(students)}")
    print(f"现有教师: {len(teachers)}")
    
    # 生成5000门课程
    print("生成课程...")
    courses_created = 0
    for i in range(5000):
        if i % 1000 == 0:
            print(f"课程进度: {i}/5000")
        
        course, created = Course.objects.get_or_create(
            code=f'FAST{i+1:05d}',
            defaults={
                'name': f'快速课程{i+1}',
                'course_type': random.choice(['required', 'elective']),
                'credits': random.choice([2, 3, 4]),
                'hours': 48,
                'department': '计算机学院',
                'semester': '2024-2025-1',
                'academic_year': '2024-2025',
                'max_students': 100,
                'min_students': 20,
            }
        )
        
        if created:
            courses_created += 1
            if teachers:
                teacher = random.choice(teachers)
                course.teachers.add(teacher)
    
    print(f"创建课程: {courses_created}")
    
    # 生成100000条选课记录
    print("生成选课记录...")
    all_courses = list(Course.objects.all())
    enrollments_created = 0
    
    for i in range(100000):
        if i % 10000 == 0:
            print(f"选课进度: {i}/100000")
        
        try:
            student = random.choice(students)
            course = random.choice(all_courses)
            
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={'status': 'enrolled'}
            )
            
            if created:
                enrollments_created += 1
        except:
            continue

print(f"完成! 选课记录: {enrollments_created}")

# 最终统计
final_students = User.objects.filter(user_type='student').count()
final_teachers = User.objects.filter(user_type='teacher').count()
final_courses = Course.objects.count()
final_enrollments = Enrollment.objects.count()

print(f"最终统计:")
print(f"学生: {final_students}")
print(f"教师: {final_teachers}")
print(f"课程: {final_courses}")
print(f"选课: {final_enrollments}")

# 保存结果到文件
with open('/app/final_result.txt', 'w') as f:
    f.write(f"学生: {final_students}\n")
    f.write(f"教师: {final_teachers}\n")
    f.write(f"课程: {final_courses}\n")
    f.write(f"选课: {final_enrollments}\n")

print("结果已保存到 /app/final_result.txt")