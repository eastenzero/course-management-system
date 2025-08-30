#!/usr/bin/env python
import os
import sys
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment

User = get_user_model()

def test_enrollment_import():
    # 读取JSON数据
    json_file = '../data-generator/output/json/course_data_20250814_135816.json'
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    enrollments = data.get('enrollments', [])
    students = data.get('students', [])
    courses = data.get('courses', [])
    
    print(f"JSON中的选课记录数量: {len(enrollments)}")
    print(f"JSON中的学生数量: {len(students)}")
    print(f"JSON中的课程数量: {len(courses)}")
    
    # 创建ID映射
    student_id_map = {}
    course_id_map = {}
    
    # 建立学生ID映射
    for student_data in students:
        try:
            user = User.objects.get(student_id=student_data['student_id'])
            student_id_map[student_data['id']] = user.id
        except User.DoesNotExist:
            pass
    
    # 建立课程ID映射
    for course_data in courses:
        try:
            course = Course.objects.get(code=course_data['code'])
            course_id_map[course_data['id']] = course.id
        except Course.DoesNotExist:
            pass
    
    print(f"学生ID映射数量: {len(student_id_map)}")
    print(f"课程ID映射数量: {len(course_id_map)}")
    
    # 测试前几条选课记录
    success_count = 0
    for i, enrollment_data in enumerate(enrollments[:10]):
        student_db_id = student_id_map.get(enrollment_data['student_id'])
        course_db_id = course_id_map.get(enrollment_data['course_id'])
        
        print(f"选课记录 {i+1}:")
        print(f"  原始学生ID: {enrollment_data['student_id']} -> 数据库ID: {student_db_id}")
        print(f"  原始课程ID: {enrollment_data['course_id']} -> 数据库ID: {course_db_id}")
        
        if student_db_id and course_db_id:
            try:
                student = User.objects.get(id=student_db_id)
                course = Course.objects.get(id=course_db_id)
                
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'status': 'enrolled',
                        'is_active': True
                    }
                )
                if created:
                    success_count += 1
                    print(f"  成功创建选课记录")
                else:
                    print(f"  选课记录已存在")
            except Exception as e:
                print(f"  创建失败: {e}")
        else:
            print(f"  映射失败")
        print()
    
    print(f"测试结果: 成功创建 {success_count} 条选课记录")

if __name__ == '__main__':
    test_enrollment_import()
