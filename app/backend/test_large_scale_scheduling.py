#!/usr/bin/env python
"""
大规模数据排课测试脚本
用于测试排课算法在大规模数据下的性能
"""

import os
import sys
import django
import random
from datetime import datetime

# 添加项目路径
sys.path.append('/root/code/course-management-system/course-management-system/backend')

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Department
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import TimeSlot
from apps.schedules.algorithms import create_auto_schedule
from apps.schedules.genetic_algorithm import create_genetic_schedule
from apps.schedules.hybrid_algorithm import create_hybrid_schedule

User = get_user_model()


def create_test_data(num_courses=1000, num_teachers=100, num_classrooms=50):
    """创建测试数据"""
    print(f"🧪 创建测试数据: {num_courses}门课程, {num_teachers}名教师, {num_classrooms}间教室")
    
    # 创建院系
    department, _ = Department.objects.get_or_create(
        name="计算机科学与技术学院",
        code="CS",
        defaults={"description": "计算机科学与技术学院"}
    )
    
    # 创建教学楼
    building, _ = Building.objects.get_or_create(
        name="教学楼A",
        code="A",
        defaults={"description": "主教学楼"}
    )
    
    # 创建时间段
    time_slots_data = [
        ("第1节", "08:00", "08:45"),
        ("第2节", "08:55", "09:40"),
        ("第3节", "10:00", "10:45"),
        ("第4节", "10:55", "11:40"),
        ("第5节", "14:00", "14:45"),
        ("第6节", "14:55", "15:40"),
        ("第7节", "16:00", "16:45"),
        ("第8节", "16:55", "17:40"),
        ("第9节", "19:00", "19:45"),
        ("第10节", "19:55", "20:40"),
    ]
    
    for i, (name, start, end) in enumerate(time_slots_data, 1):
        TimeSlot.objects.get_or_create(
            name=name,
            defaults={
                "start_time": start,
                "end_time": end,
                "order": i,
                "is_active": True
            }
        )
    
    # 创建教师
    teachers = []
    for i in range(num_teachers):
        username = f"teacher_{i:04d}"
        teacher, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": f"教师{i}",
                "last_name": "",
                "email": f"teacher{i}@example.com",
                "user_type": "teacher"
            }
        )
        teachers.append(teacher)
    
    # 创建教室
    classrooms = []
    for i in range(num_classrooms):
        room_number = f"{100 + i}"
        classroom, created = Classroom.objects.get_or_create(
            room_number=room_number,
            building=building,
            defaults={
                "capacity": random.choice([30, 50, 80, 120, 200]),
                "room_type": random.choice(["lecture", "lab", "seminar"]),
                "is_active": True,
                "is_available": True
            }
        )
        classrooms.append(classroom)
    
    # 创建课程
    course_types = ["required", "elective", "lab", "lecture"]
    for i in range(num_courses):
        course_code = f"CS{i:04d}"
        course, created = Course.objects.get_or_create(
            code=course_code,
            semester="2024春",
            academic_year="2023-2024",
            defaults={
                "name": f"计算机课程{i}",
                "department": department,
                "credits": random.choice([1, 2, 3, 4]),
                "course_type": random.choice(course_types),
                "hours": random.choice([16, 32, 48, 64]),
                "max_students": random.choice([30, 50, 80, 120]),
                "is_active": True,
                "is_published": True
            }
        )
        
        # 为课程分配教师
        if created and teachers:
            teacher = random.choice(teachers)
            course.teachers.add(teacher)
    
    print("✅ 测试数据创建完成")


def test_large_scale_scheduling():
    """测试大规模排课"""
    print("🚀 开始大规模排课测试...")
    print("=" * 60)
    
    # 测试参数
    semester = "2024春"
    academic_year = "2023-2024"
    
    # 获取课程数量
    total_courses = Course.objects.filter(
        semester=semester,
        academic_year=academic_year,
        is_active=True,
        is_published=True
    ).count()
    
    print(f"📊 测试数据规模: {total_courses}门课程")
    
    # 测试贪心算法
    print("🧠 测试贪心算法...")
    try:
        start_time = datetime.now()
        greedy_result = create_auto_schedule(
            semester, academic_year, 
            algorithm_type='greedy', 
            timeout_seconds=300
        )
        greedy_time = (datetime.now() - start_time).total_seconds()
        print(f"  ✅ 贪心算法完成: 成功率 {greedy_result['success_rate']:.1f}%, "
              f"耗时 {greedy_time:.2f}秒")
    except Exception as e:
        print(f"  ❌ 贪心算法失败: {e}")
    
    # 测试遗传算法（小规模）
    print("🧬 测试遗传算法...")
    try:
        # 限制课程数量以避免超时
        course_ids = list(Course.objects.filter(
            semester=semester,
            academic_year=academic_year,
            is_active=True,
            is_published=True
        ).values_list('id', flat=True)[:100])  # 只取前100门课程
        
        start_time = datetime.now()
        genetic_result = create_genetic_schedule(semester, academic_year, course_ids)
        genetic_time = (datetime.now() - start_time).total_seconds()
        print(f"  ✅ 遗传算法完成: 成功率 {genetic_result['success_rate']:.1f}%, "
              f"耗时 {genetic_time:.2f}秒")
    except Exception as e:
        print(f"  ❌ 遗传算法失败: {e}")
    
    # 测试混合算法（小规模）
    print("🔄 测试混合算法...")
    try:
        # 限制课程数量以避免超时
        course_ids = list(Course.objects.filter(
            semester=semester,
            academic_year=academic_year,
            is_active=True,
            is_published=True
        ).values_list('id', flat=True)[:50])  # 只取前50门课程
        
        start_time = datetime.now()
        hybrid_result = create_hybrid_schedule(semester, academic_year, course_ids)
        hybrid_time = (datetime.now() - start_time).total_seconds()
        print(f"  ✅ 混合算法完成: 成功率 {hybrid_result['success_rate']:.1f}%, "
              f"耗时 {hybrid_time:.2f}秒")
    except Exception as e:
        print(f"  ❌ 混合算法失败: {e}")
    
    print("=" * 60)
    print("✅ 大规模排课测试完成")


def cleanup_test_data():
    """清理测试数据"""
    print("🧹 清理测试数据...")
    
    # 删除测试创建的课程
    Course.objects.filter(
        code__startswith="CS",
        semester="2024春",
        academic_year="2023-2024"
    ).delete()
    
    # 删除测试创建的教师
    User.objects.filter(
        username__startswith="teacher_",
        user_type="teacher"
    ).delete()
    
    print("✅ 测试数据清理完成")


def main():
    """主函数"""
    print("🎯 大规模排课算法测试套件")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 创建测试数据
        create_test_data(num_courses=1000, num_teachers=100, num_classrooms=50)
        print()
        
        # 运行大规模排课测试
        test_large_scale_scheduling()
        print()
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    finally:
        # 清理测试数据
        cleanup_test_data()
    
    print()
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 大规模测试完成!")


if __name__ == "__main__":
    main()