#!/usr/bin/env python3
"""
导入大规模生成数据到Django数据库的脚本
"""

import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings.production_new')

# 初始化Django
django.setup()

# 导入Django模型
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.students.models import Profile as StudentProfile
from apps.teachers.models import Profile as TeacherProfile
from apps.classrooms.models import Classroom
from django.db import transaction
from django.core.exceptions import IntegrityError

User = get_user_model()

def load_data_from_json(json_file_path: str):
    """从JSON文件加载数据"""
    print(f"📂 加载数据文件: {json_file_path}")
    
    if not Path(json_file_path).exists():
        raise FileNotFoundError(f"数据文件不存在: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 数据文件加载成功")
    print(f"📊 数据统计:")
    for key, value in data.items():
        if isinstance(value, list):
            print(f"   {key}: {len(value):,} 条记录")
    
    return data

def import_users_and_profiles(students_data, teachers_data):
    """导入用户和档案数据"""
    print(f"\n👥 开始导入用户数据...")
    
    # 批量创建用户
    users_to_create = []
    student_profiles_to_create = []
    teacher_profiles_to_create = []
    
    print(f"   📝 准备学生用户数据...")
    for student in students_data:
        # 创建用户对象
        user = User(
            username=student['username'],
            email=student['email'],
            first_name=student['first_name'],
            last_name=student['last_name'],
            user_type='student',
            is_active=True
        )
        user.set_password('password123')  # 设置默认密码
        users_to_create.append(user)
    
    print(f"   📝 准备教师用户数据...")
    for teacher in teachers_data:
        user = User(
            username=teacher['username'],
            email=teacher['email'],
            first_name=teacher['first_name'],
            last_name=teacher['last_name'],
            user_type='teacher',
            is_active=True
        )
        user.set_password('password123')
        users_to_create.append(user)
    
    print(f"   💾 批量创建 {len(users_to_create):,} 个用户...")
    try:
        with transaction.atomic():
            User.objects.bulk_create(users_to_create, batch_size=1000, ignore_conflicts=True)
        print(f"   ✅ 用户创建完成")
    except Exception as e:
        print(f"   ❌ 用户创建失败: {e}")
        return False
    
    # 获取创建的用户并创建档案
    print(f"   📋 创建学生档案...")
    student_usernames = [s['username'] for s in students_data]
    student_users = {u.username: u for u in User.objects.filter(username__in=student_usernames)}
    
    for student in students_data:
        if student['username'] in student_users:
            user = student_users[student['username']]
            profile = StudentProfile(
                user=user,
                student_id=student['student_id'],
                major_name=student.get('major', '未指定专业'),
                year=student.get('year', 1),
                phone=student.get('phone', ''),
                address=student.get('address', '')
            )
            student_profiles_to_create.append(profile)
    
    print(f"   📋 创建教师档案...")
    teacher_usernames = [t['username'] for t in teachers_data]
    teacher_users = {u.username: u for u in User.objects.filter(username__in=teacher_usernames)}
    
    for teacher in teachers_data:
        if teacher['username'] in teacher_users:
            user = teacher_users[teacher['username']]
            profile = TeacherProfile(
                user=user,
                employee_id=teacher['employee_id'],
                department_name=teacher.get('department', '未指定院系'),
                title=teacher.get('title', '讲师'),
                phone=teacher.get('phone', ''),
                office=teacher.get('office', '')
            )
            teacher_profiles_to_create.append(profile)
    
    try:
        with transaction.atomic():
            StudentProfile.objects.bulk_create(student_profiles_to_create, batch_size=1000, ignore_conflicts=True)
            TeacherProfile.objects.bulk_create(teacher_profiles_to_create, batch_size=1000, ignore_conflicts=True)
        print(f"   ✅ 档案创建完成: {len(student_profiles_to_create):,} 学生档案, {len(teacher_profiles_to_create):,} 教师档案")
    except Exception as e:
        print(f"   ❌ 档案创建失败: {e}")
        return False
    
    return True

def import_courses(courses_data):
    """导入课程数据"""
    print(f"\n📚 开始导入课程数据...")
    
    courses_to_create = []
    
    for course in courses_data:
        # 查找教师用户
        teacher_user = None
        if 'teacher_username' in course:
            try:
                teacher_user = User.objects.get(username=course['teacher_username'])
            except User.DoesNotExist:
                pass
        
        course_obj = Course(
            name=course['name'],
            code=course['code'],
            credits=course.get('credits', 3),
            description=course.get('description', ''),
            course_type=course.get('type', 'elective'),
            teacher=teacher_user,
            max_students=course.get('max_students', 100),
            semester=course.get('semester', '2024-1'),
            is_active=True
        )
        courses_to_create.append(course_obj)
    
    try:
        with transaction.atomic():
            Course.objects.bulk_create(courses_to_create, batch_size=1000, ignore_conflicts=True)
        print(f"   ✅ 课程创建完成: {len(courses_to_create):,} 门课程")
    except Exception as e:
        print(f"   ❌ 课程创建失败: {e}")
        return False
    
    return True

def import_enrollments(enrollments_data):
    """导入选课记录"""
    print(f"\n🎯 开始导入选课记录...")
    
    # 获取所有用户和课程的映射
    print(f"   📋 构建用户和课程映射...")
    users_map = {u.id: u for u in User.objects.filter(user_type='student')}
    courses_map = {c.id: c for c in Course.objects.all()}
    
    enrollments_to_create = []
    valid_enrollments = 0
    
    print(f"   🔍 处理选课记录...")
    for i, enrollment in enumerate(enrollments_data):
        if i % 10000 == 0 and i > 0:
            print(f"      进度: {i:,}/{len(enrollments_data):,} ({i/len(enrollments_data)*100:.1f}%)")
        
        student_id = enrollment.get('student_id')
        course_id = enrollment.get('course_id')
        
        # 验证学生和课程是否存在
        if student_id in users_map and course_id in courses_map:
            enrollment_obj = Enrollment(
                student=users_map[student_id],
                course=courses_map[course_id],
                enrollment_date=datetime.now().date(),
                status='enrolled'
            )
            enrollments_to_create.append(enrollment_obj)
            valid_enrollments += 1
            
            # 分批处理避免内存问题
            if len(enrollments_to_create) >= 5000:
                try:
                    with transaction.atomic():
                        Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
                    enrollments_to_create = []
                except Exception as e:
                    print(f"      ⚠️ 批次导入警告: {e}")
    
    # 处理剩余的记录
    if enrollments_to_create:
        try:
            with transaction.atomic():
                Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
        except Exception as e:
            print(f"   ⚠️ 最后批次导入警告: {e}")
    
    print(f"   ✅ 选课记录导入完成: {valid_enrollments:,} 条有效记录")
    return True

def main():
    """主函数"""
    print("🚀 开始大规模数据导入")
    print("="*80)
    
    # 检查数据文件 - 使用相对路径
    json_file = "../data-generator/conservative_large_output/json/course_data_20250830_161558.json"
    
    try:
        # 加载数据
        data = load_data_from_json(json_file)
        
        # 导入用户和档案
        if not import_users_and_profiles(data['students'], data['teachers']):
            print("❌ 用户导入失败")
            return False
        
        # 导入课程
        if not import_courses(data['courses']):
            print("❌ 课程导入失败")
            return False
        
        # 导入选课记录
        if not import_enrollments(data['enrollments']):
            print("❌ 选课记录导入失败")
            return False
        
        print("\n🎉 数据导入完成！")
        
        # 显示最终统计
        print(f"\n📊 导入统计:")
        print(f"   用户总数: {User.objects.count():,}")
        print(f"   学生档案: {StudentProfile.objects.count():,}")
        print(f"   教师档案: {TeacherProfile.objects.count():,}")
        print(f"   课程总数: {Course.objects.count():,}")
        print(f"   选课记录: {Enrollment.objects.count():,}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ 大规模数据导入成功完成")
    else:
        print("❌ 数据导入任务失败")
        sys.exit(1)