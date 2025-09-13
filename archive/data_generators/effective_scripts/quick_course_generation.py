#!/usr/bin/env python
"""
快速生成课程和选课数据
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from django.db import transaction
import random

User = get_user_model()

def generate_courses_and_enrollments():
    print("📖 快速生成课程和选课数据...")
    
    DEPARTMENTS = ['计算机科学与技术学院', '数学学院', '物理学院', '化学学院', '经济学院']
    COURSE_NAMES = [
        'Python程序设计', '数据结构', '计算机网络', '数据库原理', '操作系统',
        '软件工程', '机器学习', '人工智能', 'Web开发', '移动开发',
        '高等数学', '线性代数', '概率统计', '离散数学', '数值分析',
        '大学物理', '理论力学', '电磁学', '量子力学', '热力学',
        '无机化学', '有机化学', '物理化学', '分析化学', '生物化学',
        '微观经济学', '宏观经济学', '计量经济学', '金融学', '管理学'
    ]
    
    with transaction.atomic():
        # 生成课程
        print("📖 生成课程...")
        teachers = list(User.objects.filter(user_type='teacher'))
        courses = []
        
        for i in range(10000):  # 生成10000门课程
            if i % 1000 == 0:
                print(f"   课程进度: {i}/10000")
            
            course_name = random.choice(COURSE_NAMES)
            course_code = f'COURSE{i+1:06d}'
            
            course, created = Course.objects.get_or_create(
                code=course_code,
                defaults={
                    'name': f'{course_name}_{i//len(COURSE_NAMES)+1}',
                    'course_type': random.choice(['required', 'elective', 'public']),
                    'credits': random.choice([2, 3, 4, 5]),
                    'hours': random.choice([32, 48, 64, 80]),
                    'department': random.choice(DEPARTMENTS),
                    'semester': '2024-2025-1',
                    'academic_year': '2024-2025',
                    'description': f'{course_name}课程描述',
                    'max_students': random.randint(50, 200),
                    'min_students': random.randint(10, 50),
                }
            )
            
            if created:
                courses.append(course)
                # 为课程分配教师
                if teachers:
                    selected_teachers = random.sample(teachers, min(random.randint(1, 2), len(teachers)))
                    course.teachers.set(selected_teachers)
        
        print("📝 生成选课记录...")
        students = list(User.objects.filter(user_type='student'))
        all_courses = list(Course.objects.all())
        enrollment_count = 0
        
        # 为每个学生随机选择课程
        for i, student in enumerate(students):
            if i % 2000 == 0:
                print(f"   选课进度: {i}/{len(students)}")
            
            # 每个学生选择5-8门课程
            num_courses = random.randint(5, 8)
            
            if all_courses:
                selected_courses = random.sample(all_courses, min(num_courses, len(all_courses)))
                
                for course in selected_courses:
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        course=course,
                        defaults={
                            'status': 'enrolled',
                            'score': None,
                            'grade': '',
                        }
                    )
                    
                    if created:
                        enrollment_count += 1
    
    # 统计结果
    print("\n" + "="*60)
    print("🎉 课程和选课数据生成完成!")
    print(f"📊 统计结果:")
    print(f"   - 学生用户: {User.objects.filter(user_type='student').count():,}")
    print(f"   - 教师用户: {User.objects.filter(user_type='teacher').count():,}")
    print(f"   - 课程数量: {Course.objects.count():,}")
    print(f"   - 选课记录: {Enrollment.objects.count():,}")
    print("="*60)

if __name__ == '__main__':
    generate_courses_and_enrollments()