#!/usr/bin/env python
"""
生成演示用的"百万级"数据 - 适合演示环境
生成10000用户作为百万级数据的演示版本
"""

import os
import sys
import django
import random
from datetime import datetime, date
from faker import Faker

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()
fake = Faker('zh_CN')  # 中文数据

def generate_demo_mega_data():
    """生成演示用的大量数据"""
    print("🚀 开始生成演示百万级数据...")
    print("=" * 60)
    
    # 配置数据量 (适合演示)
    STUDENT_COUNT = 8000    # 8千学生
    TEACHER_COUNT = 200     # 200教师
    COURSE_COUNT = 500      # 500课程
    ENROLLMENT_COUNT = 15000 # 1.5万选课记录
    
    BATCH_SIZE = 500        # 批次大小
    
    print(f"📊 数据规模配置:")
    print(f"   学生数量: {STUDENT_COUNT:,}")
    print(f"   教师数量: {TEACHER_COUNT:,}")
    print(f"   课程数量: {COURSE_COUNT:,}")
    print(f"   选课记录: {ENROLLMENT_COUNT:,}")
    print(f"   批次大小: {BATCH_SIZE}")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 清理现有数据
    print("🧹 清理现有大规模测试数据...")
    User.objects.filter(username__startswith='mega_student_').delete()
    User.objects.filter(username__startswith='mega_teacher_').delete()
    Course.objects.filter(name__startswith='MEGA_').delete()
    
    # 生成学生
    print(f"\n👥 生成 {STUDENT_COUNT:,} 名学生...")
    student_password = make_password('student123')
    majors = ['计算机科学', '软件工程', '信息管理', '数据科学', '人工智能', '网络工程']
    departments = ['计算机学院', '软件学院', '信息学院', '人工智能学院']
    
    created_students = 0
    for i in range(0, STUDENT_COUNT, BATCH_SIZE):
        batch_size = min(BATCH_SIZE, STUDENT_COUNT - i)
        users_to_create = []
        
        for j in range(batch_size):
            student_id = f"mega_student_{i+j+1:06d}"
            name = fake.name()
            
            user = User(
                username=student_id,
                email=f"{student_id}@university.edu.cn",
                first_name=name.split()[0] if name else "学生",
                last_name=name.split()[-1] if len(name.split()) > 1 else "",
                user_type='student',
                department=random.choice(departments),
                student_id=student_id,
                phone=fake.phone_number(),
                password=student_password,
                is_active=True
            )
            users_to_create.append(user)
        
        try:
            with transaction.atomic():
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                created_students += len(users_to_create)
                print(f"   📈 已创建 {created_students:,} 名学生...")
        except Exception as e:
            print(f"   ⚠️ 批次创建失败: {e}")
    
    # 生成教师
    print(f"\n👨‍🏫 生成 {TEACHER_COUNT:,} 名教师...")
    teacher_password = make_password('teacher123')
    created_teachers = 0
    
    for i in range(0, TEACHER_COUNT, BATCH_SIZE):
        batch_size = min(BATCH_SIZE, TEACHER_COUNT - i)
        users_to_create = []
        
        for j in range(batch_size):
            teacher_id = f"mega_teacher_{i+j+1:04d}"
            name = fake.name()
            
            user = User(
                username=teacher_id,
                email=f"{teacher_id}@university.edu.cn",
                first_name=name.split()[0] if name else "教师",
                last_name=name.split()[-1] if len(name.split()) > 1 else "",
                user_type='teacher',
                department=random.choice(departments),
                employee_id=teacher_id,
                phone=fake.phone_number(),
                password=teacher_password,
                is_active=True
            )
            users_to_create.append(user)
        
        try:
            with transaction.atomic():
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                created_teachers += len(users_to_create)
                print(f"   📈 已创建 {created_teachers:,} 名教师...")
        except Exception as e:
            print(f"   ⚠️ 批次创建失败: {e}")
    
    # 生成课程
    print(f"\n📚 生成 {COURSE_COUNT:,} 门课程...")
    subjects = ['计算机基础', '编程语言', '数据结构', '算法设计', '数据库', '网络技术', 
               '软件工程', '人工智能', '机器学习', '云计算', '大数据', '网络安全']
    levels = ['入门', '基础', '进阶', '高级']
    
    teachers = list(User.objects.filter(user_type='teacher', username__startswith='mega_teacher_'))
    created_courses = 0
    
    for i in range(0, COURSE_COUNT, BATCH_SIZE):
        batch_size = min(BATCH_SIZE, COURSE_COUNT - i)
        courses_to_create = []
        
        for j in range(batch_size):
            course_code = f"MEGA_{i+j+1:04d}"
            subject = random.choice(subjects)
            level = random.choice(levels)
            
            course = Course(
                code=course_code,
                name=f"MEGA_{subject}_{level}_{i+j+1}",
                description=f"{level}{subject}课程 - 百万级数据演示课程",
                credits=random.choice([2, 3, 4]),
                max_capacity=random.randint(30, 100),
                instructor=random.choice(teachers) if teachers else None,
                department=random.choice(departments),
                semester='2024秋季',
                academic_year='2024-2025',
                is_active=True
            )
            courses_to_create.append(course)
        
        try:
            with transaction.atomic():
                Course.objects.bulk_create(courses_to_create, ignore_conflicts=True)
                created_courses += len(courses_to_create)
                print(f"   📈 已创建 {created_courses:,} 门课程...")
        except Exception as e:
            print(f"   ⚠️ 批次创建失败: {e}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("🎉 演示百万级数据生成完成！")
    print("=" * 60)
    print(f"📊 生成统计:")
    print(f"   学生用户: {created_students:,}")
    print(f"   教师用户: {created_teachers:,}")
    print(f"   课程数量: {created_courses:,}")
    print(f"   总用户数: {created_students + created_teachers:,}")
    print(f"⏱️  生成耗时: {duration:.1f} 秒")
    print(f"⚡ 平均速度: {(created_students + created_teachers + created_courses) / duration:.0f} 记录/秒")
    
    # 验证数据
    print(f"\n🔍 数据验证:")
    total_users = User.objects.count()
    mega_users = User.objects.filter(username__startswith='mega_').count()
    total_courses = Course.objects.count()
    mega_courses = Course.objects.filter(name__startswith='MEGA_').count()
    
    print(f"   数据库中总用户数: {total_users:,}")
    print(f"   百万级演示用户: {mega_users:,}")
    print(f"   数据库中总课程数: {total_courses:,}")
    print(f"   百万级演示课程: {mega_courses:,}")
    
    return {
        'students': created_students,
        'teachers': created_teachers,
        'courses': created_courses,
        'total_records': created_students + created_teachers + created_courses,
        'duration': duration,
        'speed': (created_students + created_teachers + created_courses) / duration
    }

if __name__ == '__main__':
    try:
        results = generate_demo_mega_data()
        print(f"\n✅ 数据生成成功完成！")
    except Exception as e:
        print(f"\n❌ 数据生成失败: {e}")
        import traceback
        traceback.print_exc()