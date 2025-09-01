#!/usr/bin/env python
"""
检查数据库实际数据量
"""

# 设置环境变量，禁用有问题的模块
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'course_management.settings'
os.environ['DISABLE_MAGIC'] = '1'  # 禁用magic模块

import sys
import django

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# 修改magic模块导入问题
import builtins
original_import = builtins.__import__

def patched_import(name, *args, **kwargs):
    if name == 'magic':
        # 创建一个虚拟magic模块
        class FakeMagic:
            def from_buffer(self, buffer, mime=False):
                return 'application/octet-stream'
        
        class MockMagic:
            Magic = FakeMagic
            
        return MockMagic()
    return original_import(name, *args, **kwargs)

builtins.__import__ = patched_import

try:
    django.setup()
except Exception as e:
    print(f"警告: Django初始化问题: {e}")
    print("尝试继续运行...")

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile

User = get_user_model()

def check_database_scale():
    print('='*60)
    print('📊 数据库实际数据量检查')
    print('='*60)

    # 用户数据统计
    total_users = User.objects.count()
    students = User.objects.filter(user_type='student').count()
    teachers = User.objects.filter(user_type='teacher').count()
    admins = User.objects.filter(user_type='admin').count()
    mega_users = User.objects.filter(username__startswith='mega_').count()

    print(f'👥 用户数据:')
    print(f'   总用户数: {total_users:,}')
    print(f'   学生用户: {students:,}')
    print(f'   教师用户: {teachers:,}')
    print(f'   管理员用户: {admins:,}')
    print(f'   百万级演示用户: {mega_users:,}')

    # 课程数据统计
    total_courses = Course.objects.count()
    mega_courses = Course.objects.filter(name__startswith='MEGA_').count()

    print(f'\n📚 课程数据:')
    print(f'   总课程数: {total_courses:,}')
    print(f'   百万级演示课程: {mega_courses:,}')

    # 选课数据统计
    total_enrollments = Enrollment.objects.count()

    print(f'\n📝 选课数据:')
    print(f'   总选课记录: {total_enrollments:,}')

    # 档案数据统计
    student_profiles = StudentProfile.objects.count()
    teacher_profiles = TeacherProfile.objects.count()

    print(f'\n📋 档案数据:')
    print(f'   学生档案: {student_profiles:,}')
    print(f'   教师档案: {teacher_profiles:,}')

    # 计算总记录数
    total_records = total_users + total_courses + total_enrollments + student_profiles + teacher_profiles

    print(f'\n🔢 总记录数统计:')
    print(f'   所有表总记录数: {total_records:,}')

    # 判断是否达到百万级
    is_million_scale = total_records >= 1000000

    print(f'\n🎯 百万级评估:')
    if is_million_scale:
        print(f'   是否达到百万级(>=1,000,000): ✅ 是')
    else:
        print(f'   是否达到百万级(>=1,000,000): ❌ 否')
        print(f'   距离百万级还需: {1000000 - total_records:,} 条记录')

    print('='*60)
    
    return {
        'total_records': total_records,
        'is_million_scale': is_million_scale,
        'breakdown': {
            'users': total_users,
            'courses': total_courses, 
            'enrollments': total_enrollments,
            'student_profiles': student_profiles,
            'teacher_profiles': teacher_profiles
        }
    }

if __name__ == '__main__':
    result = check_database_scale()
    print(f"\n返回结果: {result}")