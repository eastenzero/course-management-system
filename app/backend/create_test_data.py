#!/usr/bin/env python
"""
创建测试数据的脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_settings')
django.setup()

from apps.courses.models import Course
from apps.classrooms.models import Classroom, Building
from apps.users.models import User
from django.contrib.auth.hashers import make_password

def create_test_data():
    print("开始创建测试数据...")
    
    # 创建建筑
    building1, created = Building.objects.get_or_create(
        name="教学楼A",
        defaults={
            'code': 'A',
            'description': '主教学楼',
            'address': '校园中心区域',
            'is_active': True
        }
    )
    if created:
        print(f"创建建筑: {building1.name}")

    building2, created = Building.objects.get_or_create(
        name="实验楼B", 
        defaults={
            'code': 'B',
            'description': '实验教学楼',
            'address': '校园东区',
            'is_active': True
        }
    )
    if created:
        print(f"创建建筑: {building2.name}")

    # 创建教室
    classrooms_data = [
        {'room_number': '101', 'building': building1, 'capacity': 50, 'room_type': 'lecture', 'floor': 1},
        {'room_number': '102', 'building': building1, 'capacity': 60, 'room_type': 'lecture', 'floor': 1},
        {'room_number': '201', 'building': building1, 'capacity': 40, 'room_type': 'seminar', 'floor': 2},
        {'room_number': '301', 'building': building1, 'capacity': 80, 'room_type': 'lecture', 'floor': 3},
        {'room_number': '401', 'building': building1, 'capacity': 30, 'room_type': 'seminar', 'floor': 4},
        {'room_number': '101', 'building': building2, 'capacity': 30, 'room_type': 'lab', 'floor': 1},
        {'room_number': '102', 'building': building2, 'capacity': 25, 'room_type': 'lab', 'floor': 1},
        {'room_number': '201', 'building': building2, 'capacity': 35, 'room_type': 'lab', 'floor': 2},
        {'room_number': '301', 'building': building2, 'capacity': 40, 'room_type': 'computer', 'floor': 3},
        {'room_number': '401', 'building': building2, 'capacity': 20, 'room_type': 'lab', 'floor': 4},
    ]

    for data in classrooms_data:
        classroom, created = Classroom.objects.get_or_create(
            room_number=data['room_number'],
            building=data['building'],
            defaults={
                'capacity': data['capacity'],
                'room_type': data['room_type'],
                'floor': data['floor'],
                'is_active': True,
                'is_available': True,
                'name': f"{data['building'].code}{data['room_number']}教室"
            }
        )
        if created:
            print(f"创建教室: {classroom}")

    # 创建教师用户
    teacher_user, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'email': 'teacher1@example.com',
            'first_name': '张',
            'last_name': '教授',
            'user_type': 'teacher',
            'employee_id': 'T001',  # 添加工号
            'is_active': True,
            'password': make_password('password123')
        }
    )
    if created:
        print(f"创建教师用户: {teacher_user.username}")

    # 创建更多教师
    teachers_data = [
        {'username': 'teacher2', 'first_name': '李', 'last_name': '副教授', 'employee_id': 'T002'},
        {'username': 'teacher3', 'first_name': '王', 'last_name': '讲师', 'employee_id': 'T003'},
        {'username': 'teacher4', 'first_name': '陈', 'last_name': '教授', 'employee_id': 'T004'},
    ]

    teachers = [teacher_user]
    for data in teachers_data:
        teacher, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': f"{data['username']}@example.com",
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'user_type': 'teacher',
                'employee_id': data['employee_id'],
                'is_active': True,
                'password': make_password('password123')
            }
        )
        if created:
            print(f"创建教师用户: {teacher.username}")
        teachers.append(teacher)

    # 创建课程
    courses_data = [
        {
            'name': '数据结构与算法',
            'code': 'CS101',
            'description': '计算机科学基础课程，学习各种数据结构和算法',
            'credits': 3,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[0]
        },
        {
            'name': '数据库系统',
            'code': 'CS201', 
            'description': '数据库设计与管理，SQL语言学习',
            'credits': 4,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[1] if len(teachers) > 1 else teachers[0]
        },
        {
            'name': '软件工程',
            'code': 'CS301',
            'description': '软件开发方法与实践，项目管理',
            'credits': 3,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[2] if len(teachers) > 2 else teachers[0]
        },
        {
            'name': '机器学习',
            'code': 'CS401',
            'description': '人工智能与机器学习基础，深度学习入门',
            'credits': 4,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[3] if len(teachers) > 3 else teachers[0]
        },
        {
            'name': '网络安全',
            'code': 'CS501',
            'description': '计算机网络安全技术，密码学基础',
            'credits': 3,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[0]
        },
        {
            'name': 'Web开发技术',
            'code': 'CS302',
            'description': '前端后端开发技术，框架应用',
            'credits': 3,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[1] if len(teachers) > 1 else teachers[0]
        },
        {
            'name': '操作系统',
            'code': 'CS202',
            'description': '操作系统原理与实践',
            'credits': 4,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[2] if len(teachers) > 2 else teachers[0]
        },
        {
            'name': '计算机网络',
            'code': 'CS203',
            'description': '网络协议与网络编程',
            'credits': 3,
            'semester': '2024春季',
            'department': '计算机科学系',
            'teacher': teachers[3] if len(teachers) > 3 else teachers[0]
        }
    ]

    for data in courses_data:
        course, created = Course.objects.get_or_create(
            code=data['code'],
            defaults={
                'name': data['name'],
                'description': data['description'],
                'credits': data['credits'],
                'hours': data['credits'] * 16,  # 假设每学分16学时
                'semester': data['semester'],
                'department': data['department'],
                'academic_year': '2024-2025',
                'max_students': 50,
            }
        )
        if created:
            # 添加教师
            course.teachers.add(data['teacher'])
            print(f"创建课程: {course.name}")

    # 创建学生用户
    students_data = [
        {'username': 'student1', 'first_name': '小', 'last_name': '明', 'student_id': 'S001'},
        {'username': 'student2', 'first_name': '小', 'last_name': '红', 'student_id': 'S002'},
        {'username': 'student3', 'first_name': '小', 'last_name': '华', 'student_id': 'S003'},
    ]

    for data in students_data:
        student, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': f"{data['username']}@example.com",
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'user_type': 'student',
                'student_id': data['student_id'],
                'is_active': True,
                'password': make_password('password123')
            }
        )
        if created:
            print(f"创建学生用户: {student.username}")

    # 创建管理员用户
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': '系统',
            'last_name': '管理员',
            'user_type': 'admin',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
            'password': make_password('admin123')
        }
    )
    if created:
        print(f"创建管理员用户: {admin_user.username}")

    print("测试数据创建完成!")
    print(f"创建了 {Building.objects.count()} 个建筑")
    print(f"创建了 {Classroom.objects.count()} 个教室")
    print(f"创建了 {Course.objects.count()} 个课程")
    print(f"创建了 {User.objects.filter(user_type='teacher').count()} 个教师用户")
    print(f"创建了 {User.objects.filter(user_type='student').count()} 个学生用户")
    print(f"创建了 {User.objects.filter(user_type='admin').count()} 个管理员用户")
    print("\n测试账号信息:")
    print("教师账号: teacher1 / password123")
    print("学生账号: student1 / password123")
    print("管理员账号: admin / admin123")

if __name__ == '__main__':
    create_test_data()
