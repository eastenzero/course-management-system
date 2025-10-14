#!/usr/bin/env python3
"""
将算法生成的测试数据导入到Django数据库中
"""

import os
import sys
import django
import random
from datetime import datetime, time

# 设置Django环境
sys.path.insert(0, '/root/code/course-management-system/course-management-system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

def import_test_data():
    """导入测试数据到数据库"""
    print("🚀 开始导入测试数据到数据库...")
    
    try:
        from apps.courses.models import Course
        from apps.teachers.models import TeacherProfile
        from apps.classrooms.models import Classroom, Building
        from apps.schedules.models import Schedule, TimeSlot
        from apps.users.models import User
        from django.contrib.auth import get_user_model
        from django.db import transaction
        
        User = get_user_model()
        
        with transaction.atomic():
            print("\n📚 创建课程数据...")
            
            # 课程数据 - 使用实际的Django模型结构
            courses_data = [
                # 基础课程
                {"code": "MATH101", "name": "高等数学A", "credits": 4, "hours": 64, "max_students": 120, "course_type": "required"},
                {"code": "MATH102", "name": "高等数学B", "credits": 3, "hours": 48, "max_students": 100, "course_type": "required"},
                {"code": "MATH201", "name": "线性代数", "credits": 3, "hours": 48, "max_students": 110, "course_type": "required"},
                {"code": "MATH202", "name": "概率论与数理统计", "credits": 3, "hours": 48, "max_students": 90, "course_type": "required"},
                {"code": "PHYS101", "name": "大学物理A", "credits": 4, "hours": 64, "max_students": 100, "course_type": "required"},
                {"code": "PHYS102", "name": "大学物理B", "credits": 3, "hours": 48, "max_students": 80, "course_type": "required"},
                {"code": "CS101", "name": "程序设计基础", "credits": 4, "hours": 64, "max_students": 80, "course_type": "professional"},
                {"code": "CS201", "name": "数据结构", "credits": 4, "hours": 64, "max_students": 70, "course_type": "professional"},
                {"code": "CS202", "name": "计算机组成原理", "credits": 3, "hours": 48, "max_students": 65, "course_type": "professional"},
                {"code": "CS203", "name": "操作系统", "credits": 3, "hours": 48, "max_students": 60, "course_type": "professional"},
                {"code": "CS204", "name": "数据库系统", "credits": 3, "hours": 48, "max_students": 55, "course_type": "professional"},
                {"code": "CS205", "name": "计算机网络", "credits": 3, "hours": 48, "max_students": 50, "course_type": "professional"},
                {"code": "ENG101", "name": "大学英语1", "credits": 2, "hours": 32, "max_students": 60, "course_type": "public"},
                {"code": "ENG102", "name": "大学英语2", "credits": 2, "hours": 32, "max_students": 55, "course_type": "public"},
                {"code": "PE101", "name": "体育1", "credits": 1, "hours": 16, "max_students": 100, "course_type": "public"},
            ]
            
            created_courses = []
            for course_data in courses_data:
                course, created = Course.objects.get_or_create(
                    code=course_data["code"],
                    defaults={
                        'name': course_data["name"],
                        'credits': course_data["credits"],
                        'hours': course_data["hours"],
                        'max_students': course_data["max_students"],
                        'course_type': course_data["course_type"],
                        'description': f"{course_data['name']}课程",
                        'is_active': True,
                        'is_published': True,
                    }
                )
                if created:
                    created_courses.append(course)
                    print(f"   ✓ 创建课程: {course.name}")
            
            print(f"\n👨‍🏫 创建教师数据...")
            
            # 创建用户和教师档案 - 使用实际的Django模型结构
            teacher_users_data = [
                {"username": "teacher_zhang", "email": "zhang@university.edu", "name": "张伟", "title": "professor"},
                {"username": "teacher_li", "email": "li@university.edu", "name": "李明", "title": "professor"},
                {"username": "teacher_wang", "email": "wang@university.edu", "name": "王芳", "title": "associate_professor"},
                {"username": "teacher_zhao", "email": "zhao@university.edu", "name": "赵强", "title": "associate_professor"},
                {"username": "teacher_liu", "email": "liu@university.edu", "name": "刘洋", "title": "lecturer"},
                {"username": "teacher_chen", "email": "chen@university.edu", "name": "陈静", "title": "lecturer"},
                {"username": "teacher_yang", "email": "yang@university.edu", "name": "杨帆", "title": "professor"},
                {"username": "teacher_huang", "email": "huang@university.edu", "name": "黄丽", "title": "associate_professor"},
                {"username": "teacher_sun", "email": "sun@university.edu", "name": "孙涛", "title": "lecturer"},
                {"username": "teacher_zhou", "email": "zhou@university.edu", "name": "周敏", "title": "lecturer"},
            ]
            
            created_teachers = []
            for teacher_data in teacher_users_data:
                # 创建用户 - 使用实际的User模型字段
                user, created = User.objects.get_or_create(
                    username=teacher_data["username"],
                    defaults={
                        'email': teacher_data["email"],
                        'first_name': teacher_data["name"][:1] if len(teacher_data["name"]) > 0 else "",
                        'last_name': teacher_data["name"][1:] if len(teacher_data["name"]) > 1 else "",
                        'is_active': True,
                    }
                )
                
                # 创建教师档案 - 使用实际的TeacherProfile模型结构
                teacher_profile, created = TeacherProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'title': teacher_data["title"],
                        'research_area': '计算机科学',
                        'office_location': f"理学院{random.randint(101, 999)}室",
                        'office_hours': '周一至周五 14:00-16:00',
                        'teaching_experience': random.randint(5, 20),
                        'education_background': '博士',
                        'office_phone': f"010-{random.randint(1000, 9999)}",
                        'personal_website': '',
                        'is_active_teacher': True,
                    }
                )
                
                if created:
                    created_teachers.append(teacher_profile)
                    print(f"   ✓ 创建教师: {teacher_data['name']} ({teacher_data['title']})")
            
            print(f"\n🏫 创建教室数据...")
            
            # 创建建筑 - 使用实际的Building模型结构
            buildings_data = [
                {"code": "A", "name": "教学楼A", "address": "校园东区"},
                {"code": "B", "name": "教学楼B", "address": "校园西区"},
                {"code": "C", "name": "教学楼C", "address": "校园南区"},
                {"code": "D", "name": "实验楼D", "address": "校园北区"},
            ]
            
            building_map = {}
            for building_data in buildings_data:
                building, created = Building.objects.get_or_create(
                    code=building_data["code"],
                    defaults={
                        'name': building_data["name"],
                        'address': building_data["address"],
                        'description': f"{building_data['name']}，位于{building_data['address']}",
                        'is_active': True,
                    }
                )
                building_map[building_data["code"]] = building
                if created:
                    print(f"   ✓ 创建建筑: {building.name}")
            
            # 创建教室 - 使用实际的Classroom模型结构
            classrooms_data = [
                # 大型阶梯教室
                {"room_number": "A101", "name": "教学楼A101", "building": "A", "floor": 1, "capacity": 200, "type": "auditorium"},
                {"room_number": "A102", "name": "教学楼A102", "building": "A", "floor": 1, "capacity": 180, "type": "auditorium"},
                {"room_number": "A103", "name": "教学楼A103", "building": "A", "floor": 1, "capacity": 150, "type": "auditorium"},
                # 中型多媒体教室
                {"room_number": "B201", "name": "教学楼B201", "building": "B", "floor": 2, "capacity": 120, "type": "multimedia"},
                {"room_number": "B202", "name": "教学楼B202", "building": "B", "floor": 2, "capacity": 100, "type": "multimedia"},
                {"room_number": "B203", "name": "教学楼B203", "building": "B", "floor": 2, "capacity": 80, "type": "multimedia"},
                {"room_number": "B204", "name": "教学楼B204", "building": "B", "floor": 2, "capacity": 80, "type": "multimedia"},
                # 小型研讨教室
                {"room_number": "C301", "name": "教学楼C301", "building": "C", "floor": 3, "capacity": 60, "type": "seminar"},
                {"room_number": "C302", "name": "教学楼C302", "building": "C", "floor": 3, "capacity": 50, "type": "seminar"},
                {"room_number": "C303", "name": "教学楼C303", "building": "C", "floor": 3, "capacity": 50, "type": "seminar"},
                # 计算机实验室
                {"room_number": "D401", "name": "实验楼D401", "building": "D", "floor": 4, "capacity": 70, "type": "computer"},
                {"room_number": "D402", "name": "实验楼D402", "building": "D", "floor": 4, "capacity": 60, "type": "computer"},
            ]
            
            created_classrooms = []
            for classroom_data in classrooms_data:
                classroom, created = Classroom.objects.get_or_create(
                    building=building_map[classroom_data["building"]],
                    room_number=classroom_data["room_number"],
                    defaults={
                        'name': classroom_data["name"],
                        'floor': classroom_data["floor"],
                        'capacity': classroom_data["capacity"],
                        'room_type': classroom_data["type"],
                        'equipment': {'projector': '投影仪', 'audio': '音响', 'ac': '空调'},
                        'location_description': f"{classroom_data['name']}，容量{classroom_data['capacity']}人",
                        'is_available': True,
                        'is_active': True,
                    }
                )
                if created:
                    created_classrooms.append(classroom)
                    print(f"   ✓ 创建教室: {classroom.name} (容量: {classroom.capacity})")
            
            print(f"\n📋 创建时间段数据...")
            
            # 创建时间段 - 使用实际的TimeSlot模型结构
            time_slots_data = [
                {"order": 1, "start_time": "08:00", "end_time": "08:45", "name": "第1节"},
                {"order": 2, "start_time": "08:55", "end_time": "09:40", "name": "第2节"},
                {"order": 3, "start_time": "10:00", "end_time": "10:45", "name": "第3节"},
                {"order": 4, "start_time": "10:55", "end_time": "11:40", "name": "第4节"},
                {"order": 5, "start_time": "14:00", "end_time": "14:45", "name": "第5节"},
                {"order": 6, "start_time": "14:55", "end_time": "15:40", "name": "第6节"},
                {"order": 7, "start_time": "16:00", "end_time": "16:45", "name": "第7节"},
                {"order": 8, "start_time": "16:55", "end_time": "17:40", "name": "第8节"},
            ]
            
            created_time_slots = []
            for slot_data in time_slots_data:
                time_slot, created = TimeSlot.objects.get_or_create(
                    order=slot_data["order"],
                    defaults={
                        'name': slot_data["name"],
                        'start_time': datetime.strptime(slot_data["start_time"], "%H:%M").time(),
                        'end_time': datetime.strptime(slot_data["end_time"], "%H:%M").time(),
                        'is_active': True,
                    }
                )
                if created:
                    created_time_slots.append(time_slot)
                    print(f"   ✓ 创建时间段: {time_slot.name} ({time_slot.start_time}-{time_slot.end_time})")
            
            print(f"\n🎯 数据导入完成！")
            print(f"   ✓ 创建了 {len(created_courses)} 门课程")
            print(f"   ✓ 创建了 {len(created_teachers)} 名教师")
            print(f"   ✓ 创建了 {len(created_classrooms)} 间教室")
            print(f"   ✓ 创建了 {len(created_time_slots)} 个时间段")
            
            return {
                'courses': created_courses,
                'teachers': created_teachers,
                'classrooms': created_classrooms,
                'time_slots': created_time_slots
            }
            
    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 开始导入测试数据到数据库...")
    print("="*60)
    
    result = import_test_data()
    
    if result:
        print("\n" + "="*60)
        print("🎉 数据导入成功完成！")
        print("前端现在应该能够显示最新的数据了。")
        print("="*60)
    else:
        print("\n❌ 数据导入失败")
        sys.exit(1)