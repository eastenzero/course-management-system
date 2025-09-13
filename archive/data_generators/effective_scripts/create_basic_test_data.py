#!/usr/bin/env python
"""
创建基础测试数据脚本
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from apps.users.models import User
from apps.courses.models import Course
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import TimeSlot
from django.db import transaction

def create_basic_test_data():
    print('🚀 开始创建基础测试数据...')
    
    with transaction.atomic():
        # 创建一些教师
        print('👨‍🏫 创建教师账户...')
        teachers = []
        for i in range(1, 6):
            teacher, created = User.objects.get_or_create(
                username=f'teacher{i:02d}',
                defaults={
                    'first_name': f'教师{i}',
                    'last_name': '老师',
                    'email': f'teacher{i}@university.edu',
                    'user_type': 'teacher',
                    'department': '计算机学院',
                    'is_active': True
                }
            )
            if created:
                teacher.set_password('teacher123')
                teacher.save()
                teachers.append(teacher)
                print(f'   ✅ 创建教师: {teacher.username}')
        
        # 创建一些学生
        print('👨‍🎓 创建学生账户...')
        students = []
        for i in range(1, 21):
            student, created = User.objects.get_or_create(
                username=f'student{i:03d}',
                defaults={
                    'first_name': f'学生{i}',
                    'last_name': '同学',
                    'email': f'student{i}@university.edu',
                    'user_type': 'student',
                    'student_id': f'2024{i:04d}',
                    'department': '计算机学院',
                    'is_active': True
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                students.append(student)
                if i <= 5:
                    print(f'   ✅ 创建学生: {student.username}')
        
        print(f'   ✅ 总计创建 {len(students)} 名学生')
        
        # 创建教学楼和教室
        print('🏢 创建教学楼和教室...')
        building, created = Building.objects.get_or_create(
            name='信息楼',
            defaults={
                'code': 'INFO',
                'address': '校园中心区',
                'description': '信息技术教学楼'
            }
        )
        
        classrooms = []
        for floor in range(1, 4):
            for room in range(1, 6):
                room_number = f'{floor}0{room}'
                classroom, created = Classroom.objects.get_or_create(
                    building=building,
                    room_number=room_number,
                    defaults={
                        'name': f'信息楼{room_number}',
                        'capacity': 50,
                        'room_type': 'lecture',
                        'floor': floor,
                        'equipment': {'projector': True, 'audio': True, 'ac': True},
                        'is_available': True
                    }
                )
                if created:
                    classrooms.append(classroom)
        
        print(f'   ✅ 创建 {len(classrooms)} 间教室')
        
        # 创建时间段
        print('⏰ 创建时间段...')
        time_slots_data = [
            ('第1节', '08:00', '08:45'),
            ('第2节', '08:55', '09:40'),
            ('第3节', '10:00', '10:45'),
            ('第4节', '10:55', '11:40'),
            ('第5节', '14:00', '14:45'),
            ('第6节', '14:55', '15:40'),
            ('第7节', '16:00', '16:45'),
            ('第8节', '16:55', '17:40'),
        ]
        
        time_slots = []
        for name, start, end in time_slots_data:
            slot, created = TimeSlot.objects.get_or_create(
                name=name,
                defaults={
                    'start_time': start,
                    'end_time': end,
                    'is_active': True
                }
            )
            if created:
                time_slots.append(slot)
        
        print(f'   ✅ 创建 {len(time_slots)} 个时间段')
        
        # 创建课程
        print('📚 创建课程...')
        courses_data = [
            ('Python程序设计', 'CS101', 3, '计算机基础课程'),
            ('数据结构与算法', 'CS102', 4, '计算机核心课程'),
            ('数据库系统原理', 'CS201', 3, '数据库相关课程'),
            ('Web开发技术', 'CS202', 3, 'Web前后端开发'),
            ('机器学习基础', 'CS301', 4, '人工智能入门'),
            ('软件工程', 'CS203', 3, '软件开发方法论'),
            ('计算机网络', 'CS204', 3, '网络技术基础'),
            ('操作系统', 'CS205', 4, '系统软件原理'),
        ]
        
        courses = []
        for i, (name, code, credits, desc) in enumerate(courses_data):
            teacher = teachers[i % len(teachers)] if teachers else None
            course, created = Course.objects.get_or_create(
                course_code=code,
                defaults={
                    'name': name,
                    'credits': credits,
                    'description': desc,
                    'teacher': teacher,
                    'department': '计算机学院',
                    'semester': '2024-2025-1',
                    'max_students': 50,
                    'status': 'active'
                }
            )
            if created:
                courses.append(course)
                teacher_name = teacher.first_name if teacher else '未分配'
                print(f'   ✅ 创建课程: {course.name} (教师: {teacher_name})')

    print()
    print('🎉 基础测试数据创建完成!')
    print(f'📊 数据统计:')
    print(f'   - 教师: {User.objects.filter(user_type="teacher").count()} 人')
    print(f'   - 学生: {User.objects.filter(user_type="student").count()} 人')
    print(f'   - 课程: {Course.objects.count()} 门')
    print(f'   - 教室: {Classroom.objects.count()} 间')
    print(f'   - 时间段: {TimeSlot.objects.count()} 个')
    print()
    print('🔑 测试账户信息:')
    print('   管理员: admin / admin123')
    print('   教师: teacher01-teacher05 / teacher123')
    print('   学生: student001-student020 / student123')

if __name__ == '__main__':
    create_basic_test_data()
