#!/usr/bin/env python
"""
快速生成大量数据脚本
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment
from apps.schedules.models import TimeSlot
from django.contrib.auth.hashers import make_password
from django.db import transaction
import random
from decimal import Decimal
from datetime import time

User = get_user_model()

def generate_data():
    print("🚀 开始快速生成大量数据...")
    
    # 预定义数据
    DEPARTMENTS = ['计算机科学与技术学院', '数学学院', '物理学院', '化学学院', '经济学院', '管理学院', '外语学院', '文学院', '法学院', '医学院']
    MAJORS = ['计算机科学与技术', '软件工程', '网络工程', '数学与应用数学', '物理学', '化学', '经济学', '工商管理', '英语', '汉语言文学']
    FIRST_NAMES = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴']
    LAST_NAMES = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋']
    
    def get_random_name():
        return random.choice(FIRST_NAMES) + random.choice(LAST_NAMES)
    
    with transaction.atomic():
        print("⏰ 创建时间段...")
        time_slots_data = [
            ('第1节', time(8, 0), time(8, 45), 1),
            ('第2节', time(8, 55), time(9, 40), 2),
            ('第3节', time(10, 0), time(10, 45), 3),
            ('第4节', time(10, 55), time(11, 40), 4),
            ('第5节', time(14, 0), time(14, 45), 5),
            ('第6节', time(14, 55), time(15, 40), 6),
            ('第7节', time(16, 0), time(16, 45), 7),
            ('第8节', time(16, 55), time(17, 40), 8),
        ]
        
        for name, start, end, order in time_slots_data:
            TimeSlot.objects.get_or_create(
                name=name,
                defaults={'start_time': start, 'end_time': end, 'order': order}
            )
        
        print("👨‍🏫 生成教师数据...")
        teacher_password = make_password('teacher123')
        teachers = []
        
        for i in range(5001, 10001):  # 生成5000个教师
            if i % 1000 == 0:
                print(f"   教师进度: {i-5000}/5000")
            
            username = f'teacher{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@university.edu',
                    'first_name': get_random_name(),
                    'user_type': 'teacher',
                    'employee_id': f'T{i}',
                    'department': random.choice(DEPARTMENTS),
                    'is_active': True,
                    'password': teacher_password,
                }
            )
            
            if created:
                teachers.append(user)
                TeacherProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'title': random.choice(['assistant', 'lecturer', 'associate_professor', 'professor']),
                        'research_area': f'{user.department}研究',
                        'teaching_experience': random.randint(1, 20),
                        'education_background': '博士',
                        'is_active_teacher': True,
                    }
                )
        
        print("👨‍🎓 生成学生数据...")
        student_password = make_password('student123')
        students = []
        
        # 批量生成学生，分批处理
        batch_size = 5000
        total_students = 120000  # 生成12万学生
        
        for batch_start in range(100001, 100001 + total_students, batch_size):
            batch_end = min(batch_start + batch_size, 100001 + total_students)
            print(f"   学生批次: {batch_start} - {batch_end}")
            
            for i in range(batch_start, batch_end):
                username = f'student{i}'
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@student.edu',
                        'first_name': get_random_name(),
                        'user_type': 'student',
                        'student_id': f'S{i}',
                        'department': random.choice(DEPARTMENTS),
                        'is_active': True,
                        'password': student_password,
                    }
                )
                
                if created:
                    students.append(user)
                    StudentProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'admission_year': random.choice([2021, 2022, 2023, 2024]),
                            'major': random.choice(MAJORS),
                            'class_name': f'{random.choice(MAJORS)}{random.randint(1, 5)}班',
                            'gpa': Decimal(str(round(random.uniform(2.0, 4.0), 2))),
                            'total_credits': 120,
                            'completed_credits': random.randint(20, 100),
                            'enrollment_status': 'active',
                        }
                    )
        
        print("📖 生成课程数据...")
        course_names = [
            'Python程序设计', '数据结构', '计算机网络', '数据库原理', '操作系统',
            '软件工程', '机器学习', '人工智能', 'Web开发', '移动开发',
            '高等数学', '线性代数', '概率统计', '离散数学', '数值分析',
            '大学物理', '理论力学', '电磁学', '量子力学', '热力学',
            '无机化学', '有机化学', '物理化学', '分析化学', '生物化学',
            '微观经济学', '宏观经济学', '计量经济学', '金融学', '管理学',
            '大学英语', '英语听说', '英语写作', '商务英语', '翻译理论'
        ]
        
        courses = []
        for i, course_name in enumerate(course_names * 300):  # 重复生成更多课程
            if i % 1000 == 0:
                print(f"   课程进度: {i}/10000")
            
            course_code = f'COURSE{i+1:06d}'
            course, created = Course.objects.get_or_create(
                code=course_code,
                defaults={
                    'name': f'{course_name}_{i//len(course_names)+1}',
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
                    selected_teachers = random.sample(teachers, min(random.randint(1, 3), len(teachers)))
                    course.teachers.set(selected_teachers)
        
        print("📝 生成选课记录...")
        enrollment_count = 0
        
        # 为每个学生随机选择课程
        for i, student in enumerate(User.objects.filter(user_type='student')):
            if i % 5000 == 0:
                print(f"   选课进度: {i}/{User.objects.filter(user_type='student').count()}")
            
            # 每个学生选择3-8门课程
            num_courses = random.randint(3, 8)
            available_courses = Course.objects.all()
            
            if available_courses.count() > 0:
                selected_courses = random.sample(
                    list(available_courses), 
                    min(num_courses, available_courses.count())
                )
                
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
    print("🎉 数据生成完成!")
    print(f"📊 统计结果:")
    print(f"   - 学生用户: {User.objects.filter(user_type='student').count():,}")
    print(f"   - 教师用户: {User.objects.filter(user_type='teacher').count():,}")
    print(f"   - 课程数量: {Course.objects.count():,}")
    print(f"   - 选课记录: {Enrollment.objects.count():,}")
    print(f"   - 时间段: {TimeSlot.objects.count()}")
    print("="*60)

if __name__ == '__main__':
    generate_data()