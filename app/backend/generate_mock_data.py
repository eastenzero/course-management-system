#!/usr/bin/env python3
"""
生成模拟数据脚本
用于生成课程、教师、教室等模拟数据
"""

import os
import sys
import random
import django
from datetime import time

# 添加项目路径
sys.path.append('/root/code/course-management-system/course-management-system/backend')

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import TimeSlot
from apps.users.models import User

UserModel = get_user_model()


def create_buildings_and_classrooms():
    """创建教学楼和教室"""
    print("🏢 创建教学楼和教室...")
    
    # 创建教学楼
    buildings_data = [
        {"name": "教学楼A", "code": "A", "address": "主校区中心"},
        {"name": "教学楼B", "code": "B", "address": "主校区东侧"},
        {"name": "实验楼", "code": "L", "address": "主校区西侧"},
    ]
    
    buildings = []
    for data in buildings_data:
        building, created = Building.objects.get_or_create(
            code=data["code"],
            defaults={
                "name": data["name"],
                "address": data["address"],
                "is_active": True
            }
        )
        buildings.append(building)
        if created:
            print(f"  创建教学楼: {building.name}")
    
    # 创建教室
    room_types = ["lecture", "lab", "computer", "multimedia", "seminar"]
    capacities = [30, 50, 80, 120, 200]
    
    classroom_count = 0
    for building in buildings:
        for i in range(1, random.randint(8, 15)):  # 每栋楼8-14间教室
            room_number = f"{random.randint(1, 5)}0{i:02d}"  # 楼层+房间号
            classroom, created = Classroom.objects.get_or_create(
                building=building,
                room_number=room_number,
                defaults={
                    "name": f"{building.code}-{room_number}",
                    "capacity": random.choice(capacities),
                    "room_type": random.choice(room_types),
                    "floor": int(room_number[0]),
                    "is_available": True,
                    "is_active": True
                }
            )
            if created:
                classroom_count += 1
    
    print(f"✅ 创建了 {classroom_count} 间教室")


def create_time_slots():
    """创建时间段"""
    print("⏰ 创建时间段...")
    
    from datetime import time
    
    time_slots_data = [
        ("第1节", time(8, 0), time(8, 45)),
        ("第2节", time(8, 55), time(9, 40)),
        ("第3节", time(10, 0), time(10, 45)),
        ("第4节", time(10, 55), time(11, 40)),
        ("第5节", time(14, 0), time(14, 45)),
        ("第6节", time(14, 55), time(15, 40)),
        ("第7节", time(16, 0), time(16, 45)),
        ("第8节", time(16, 55), time(17, 40)),
        ("第9节", time(19, 0), time(19, 45)),
        ("第10节", time(19, 55), time(20, 40)),
    ]
    
    created_count = 0
    for i, (name, start, end) in enumerate(time_slots_data, 1):
        time_slot, created = TimeSlot.objects.get_or_create(
            name=name,
            defaults={
                "start_time": start,
                "end_time": end,
                "order": i,
                "is_active": True
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ 创建了 {created_count} 个时间段")


def create_teachers(num_teachers=30):
    """创建教师"""
    print(f"👨‍🏫 创建 {num_teachers} 名教师...")
    
    departments = [
        "计算机科学与技术学院",
        "软件学院", 
        "信息工程学院",
        "数学与统计学院",
        "物理与电子工程学院"
    ]
    
    created_count = 0
    for i in range(num_teachers):
        username = f"teacher_{i+1:03d}"
        # 检查教师是否已存在
        if not User.objects.filter(username=username).exists():
            teacher = User.objects.create_user(
                username=username,
                email=f"teacher{i+1}@university.edu",
                first_name=f"教师{i+1}",
                last_name="",
                user_type="teacher",
                department=random.choice(departments),
                is_active=True
            )
            created_count += 1
    
    print(f"✅ 创建了 {created_count} 名教师")


def create_courses(num_courses=100):
    """创建课程"""
    print(f"📚 创建 {num_courses} 门课程...")
    
    departments = [
        ("计算机科学与技术学院", "CS"),
        ("软件学院", "SE"), 
        ("信息工程学院", "IE"),
        ("数学与统计学院", "MS"),
        ("物理与电子工程学院", "PE")
    ]
    
    course_types = ["required", "elective", "lab", "lecture"]
    credits_options = [1, 2, 3, 4]
    hours_options = [16, 32, 48, 64]
    max_students_options = [30, 50, 80, 120]
    
    # 获取所有教师
    teachers = list(User.objects.filter(user_type="teacher"))
    if not teachers:
        print("❌ 没有找到教师，请先创建教师")
        return
    
    created_count = 0
    for i in range(num_courses):
        course_code = f"{random.choice(['CS', 'SE', 'IE', 'MS', 'PE'])}{i+1:04d}"
        
        # 检查课程是否已存在
        if not Course.objects.filter(code=course_code, semester="2024-1", academic_year="2023-2024").exists():
            course = Course.objects.create(
                code=course_code,
                name=f"{random.choice(['计算机', '软件', '信息', '数学', '物理'])}课程{i+1}",
                credits=random.choice(credits_options),
                hours=random.choice(hours_options),
                course_type=random.choice(course_types),
                department=random.choice([d[0] for d in departments]),
                semester="2024-1",
                academic_year="2023-2024",
                max_students=random.choice(max_students_options),
                min_students=10,
                is_active=True,
                is_published=True
            )
            
            # 为课程分配1-3名教师
            num_teachers_for_course = random.randint(1, 3)
            selected_teachers = random.sample(teachers, min(num_teachers_for_course, len(teachers)))
            course.teachers.set(selected_teachers)
            
            created_count += 1
    
    print(f"✅ 创建了 {created_count} 门课程")


def main():
    """主函数"""
    print("🎓 开始生成模拟数据...")
    print("=" * 50)
    
    try:
        # 创建教学楼和教室
        create_buildings_and_classrooms()
        print()
        
        # 创建时间段
        create_time_slots()
        print()
        
        # 创建教师
        create_teachers(30)
        print()
        
        # 创建课程
        create_courses(100)
        print()
        
        print("=" * 50)
        print("🎉 模拟数据生成完成!")
        print()
        print("📊 数据统计:")
        print(f"  教学楼: {Building.objects.count()} 栋")
        print(f"  教室: {Classroom.objects.count()} 间")
        print(f"  时间段: {TimeSlot.objects.count()} 个")
        print(f"  教师: {User.objects.filter(user_type='teacher').count()} 名")
        print(f"  课程: {Course.objects.filter(semester='2024-1', academic_year='2023-2024').count()} 门")
        
    except Exception as e:
        print(f"❌ 生成模拟数据时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()