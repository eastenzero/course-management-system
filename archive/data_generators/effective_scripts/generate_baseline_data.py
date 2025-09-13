#!/usr/bin/env python
"""
基于170,000选课记录基准的数据生成脚本
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from django.db import transaction, connection
import random
import time

User = get_user_model()

def generate_baseline_data():
    print("🚀 基于170,000选课记录基准生成数据...")
    
    DEPARTMENTS = ['计算机科学与技术学院', '数学学院', '物理学院', '化学学院', '经济学院', '管理学院', '外语学院', '文学院', '法学院', '医学院']
    
    COURSE_NAMES = [
        'Python程序设计', '数据结构与算法', '计算机网络', '数据库系统原理', '操作系统原理',
        '软件工程', '机器学习基础', '人工智能导论', 'Web开发技术', '移动应用开发',
        '高等数学A', '线性代数', '概率论与数理统计', '离散数学', '数值分析方法',
        '大学物理', '理论力学', '电磁学基础', '量子力学导论', '热力学与统计物理',
        '无机化学', '有机化学', '物理化学', '分析化学', '生物化学基础',
        '微观经济学', '宏观经济学', '计量经济学', '金融学概论', '管理学原理',
        '大学英语', '英语听说', '英语写作', '商务英语', '英美文学选读'
    ]
    
    start_time = time.time()
    
    with transaction.atomic():
        # 获取现有用户数据
        students = list(User.objects.filter(user_type='student'))
        teachers = list(User.objects.filter(user_type='teacher'))
        
        print(f"📊 现有用户数据:")
        print(f"   - 学生: {len(students):,}人")
        print(f"   - 教师: {len(teachers):,}人")
        
        # 基于170,000选课记录计算所需课程数量
        # 假设每个学生平均选5门课: 170,000 / 5 = 34,000 个选课关系
        # 考虑到每门课程有多个学生选择，需要约 5,000-8,000 门课程
        target_courses = 6000
        target_enrollments = 170000
        
        print(f"\n🎯 目标数据量:")
        print(f"   - 目标课程数: {target_courses:,}门")
        print(f"   - 目标选课记录: {target_enrollments:,}条")
        
        # 1. 生成课程数据
        print("\n📖 生成课程数据...")
        courses_created = 0
        
        for i in range(target_courses):
            if i > 0 and i % 1000 == 0:
                print(f"   课程进度: {i:,}/{target_courses:,} ({i/target_courses*100:.1f}%)")
            
            course_name = random.choice(COURSE_NAMES)
            course_code = f'COURSE{i+1:06d}'
            
            try:
                course, created = Course.objects.get_or_create(
                    code=course_code,
                    defaults={
                        'name': f'{course_name}({i//len(COURSE_NAMES)+1})',
                        'course_type': random.choice(['required', 'elective', 'public']),
                        'credits': random.choice([2, 3, 4, 5]),
                        'hours': random.choice([32, 48, 64, 80]),
                        'department': random.choice(DEPARTMENTS),
                        'semester': '2024-2025-1',
                        'academic_year': '2024-2025',
                        'description': f'{course_name}课程，编号{i+1}',
                        'max_students': random.randint(80, 200),
                        'min_students': random.randint(20, 50),
                    }
                )
                
                if created:
                    courses_created += 1
                    # 为课程分配1-2名教师
                    if teachers:
                        num_teachers = random.randint(1, min(2, len(teachers)))
                        selected_teachers = random.sample(teachers, num_teachers)
                        course.teachers.set(selected_teachers)
                        
            except Exception as e:
                print(f"   ⚠️ 创建课程失败: {e}")
                continue
        
        print(f"   ✅ 成功创建 {courses_created:,} 门课程")
        
        # 2. 生成选课记录
        print(f"\n📝 生成 {target_enrollments:,} 条选课记录...")
        all_courses = list(Course.objects.all())
        enrollments_created = 0
        
        # 批量生成选课记录，确保达到目标数量
        batch_size = 1000
        
        for batch_start in range(0, target_enrollments, batch_size):
            batch_end = min(batch_start + batch_size, target_enrollments)
            
            if batch_start % 10000 == 0:
                print(f"   选课进度: {batch_start:,}/{target_enrollments:,} ({batch_start/target_enrollments*100:.1f}%)")
            
            # 在每个批次中创建选课记录
            for i in range(batch_start, batch_end):
                try:
                    # 随机选择学生和课程
                    student = random.choice(students)
                    course = random.choice(all_courses)
                    
                    # 检查是否已经选过这门课
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
                        enrollments_created += 1
                        
                except Exception as e:
                    # 忽略重复选课等错误，继续处理
                    continue
        
        print(f"   ✅ 成功创建 {enrollments_created:,} 条选课记录")
        
        # 3. 如果选课记录不够，继续生成
        current_enrollments = Enrollment.objects.count()
        if current_enrollments < target_enrollments:
            remaining = target_enrollments - current_enrollments
            print(f"\n🔄 需要补充 {remaining:,} 条选课记录...")
            
            additional_created = 0
            attempts = 0
            max_attempts = remaining * 3  # 最多尝试3倍数量
            
            while additional_created < remaining and attempts < max_attempts:
                attempts += 1
                
                if attempts % 5000 == 0:
                    print(f"   补充进度: {additional_created:,}/{remaining:,}")
                
                try:
                    student = random.choice(students)
                    course = random.choice(all_courses)
                    
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
                        additional_created += 1
                        
                except Exception:
                    continue
            
            print(f"   ✅ 补充创建 {additional_created:,} 条选课记录")
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    # 最终统计
    print("\n" + "="*60)
    print("🎉 数据生成完成!")
    print(f"📊 最终统计结果:")
    print(f"   - 学生用户: {User.objects.filter(user_type='student').count():,}")
    print(f"   - 教师用户: {User.objects.filter(user_type='teacher').count():,}")
    print(f"   - 课程数量: {Course.objects.count():,}")
    print(f"   - 选课记录: {Enrollment.objects.count():,}")
    print(f"   - 时间段数量: {TimeSlot.objects.count()}")
    print(f"⏱️  总耗时: {generation_time:.2f} 秒")
    print(f"🚀 生成速度: {Enrollment.objects.count()/generation_time:.0f} 条选课记录/秒")
    print("="*60)

if __name__ == '__main__':
    generate_baseline_data()