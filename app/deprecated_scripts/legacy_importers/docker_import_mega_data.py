#!/usr/bin/env python
"""
Docker环境下的百万级数据导入脚本
适配Django容器环境，支持大规模数据导入
"""

import os
import sys
import json
import django
import gc
import psutil
from datetime import datetime, date
from decimal import Decimal
import random
import time
from typing import List, Dict, Any, Iterator
from pathlib import Path

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction, connection
from django.contrib.auth.hashers import make_password
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()

class DockerImportManager:
    """Docker环境专用的导入管理器"""
    
    def __init__(self, batch_size=3000):
        self.batch_size = batch_size
        self.imported_count = 0
        self.error_count = 0
        
        # 预计算密码哈希
        self.student_password_hash = make_password('student123')
        self.teacher_password_hash = make_password('teacher123')
        
    def log_progress(self, current, total, operation="导入"):
        """记录进度"""
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"   📈 {operation}进度: {current:,}/{total:,} ({percentage:.1f}%)")
        
    def batch_create_users(self, users_data: List[Dict], user_type: str, dept_names: List[str], limit: int = None) -> int:
        """批量创建用户（支持限制数量）"""
        if limit:
            users_data = users_data[:limit]
            
        created_count = 0
        total_users = len(users_data)
        
        print(f"\n👥 开始批量创建{user_type}用户...")
        print(f"   📊 计划创建 {total_users:,} 个{user_type}用户...")
        
        for i in range(0, total_users, self.batch_size):
            batch = users_data[i:i + self.batch_size]
            
            try:
                with transaction.atomic():
                    batch_users = []
                    
                    for user_data in batch:
                        try:
                            if user_type == 'student':
                                username = f"student_{user_data['student_id']}"
                                unique_field = {'student_id': user_data['student_id']}
                            else:  # teacher
                                username = f"teacher_{user_data['employee_id']}"
                                unique_field = {'employee_id': user_data['employee_id']}
                            
                            # 检查用户是否已存在
                            if not User.objects.filter(username=username).exists():
                                user = User(
                                    username=username,
                                    email=f"{username}@university.edu.cn",
                                    first_name=user_data['name'].split()[0] if user_data['name'] else (user_type.title()),
                                    last_name=user_data['name'].split()[-1] if len(user_data['name'].split()) > 1 else '',
                                    user_type=user_type,
                                    department=random.choice(dept_names) if dept_names else '未分配',
                                    phone=user_data.get('phone', ''),
                                    is_active=user_data.get('is_active', True),
                                    password=self.student_password_hash if user_type == 'student' else self.teacher_password_hash,
                                    **unique_field
                                )
                                batch_users.append(user)
                        except Exception as e:
                            self.error_count += 1
                            continue
                    
                    # 批量创建用户
                    if batch_users:
                        created_users = User.objects.bulk_create(batch_users, ignore_conflicts=True)
                        created_count += len(batch_users)
                
                # 记录进度
                self.log_progress(min(i + self.batch_size, total_users), total_users, f"{user_type}用户创建")
                
                # 定期垃圾回收
                if i % (self.batch_size * 5) == 0:
                    gc.collect()
                    
            except Exception as e:
                print(f"   ❌ 批量创建{user_type}用户失败: {e}")
                self.error_count += len(batch)
                continue
        
        print(f"   ✅ 成功创建 {created_count:,} 个{user_type}用户")
        return created_count
    
    def create_user_profiles(self, user_type: str, users_data: List[Dict], majors_data: List[Dict] = None, limit: int = None):
        """创建用户档案（支持限制数量）"""
        print(f"\n📋 创建{user_type}档案...")
        
        if user_type == 'student':
            major_map = {major['id']: major['name'] for major in majors_data} if majors_data else {}
            users = User.objects.filter(user_type='student').order_by('id')
            
            if limit:
                users = users[:limit]
                users_data = users_data[:limit]
            
            total_users = users.count()
            profiles_to_create = []
            
            user_list = list(users)
            for i, user in enumerate(user_list):
                if i < len(users_data):
                    student_data = users_data[i]
                    major_name = major_map.get(student_data.get('major_id'), '未分配专业')
                    
                    if not StudentProfile.objects.filter(user=user).exists():
                        profile = StudentProfile(
                            user=user,
                            admission_year=student_data.get('grade', 2024),
                            major=major_name,
                            class_name=f"{major_name}{student_data.get('class_number', 1)}班",
                            gpa=Decimal(str(student_data.get('gpa', 0.0))),
                            total_credits=student_data.get('total_credits', 0),
                            completed_credits=student_data.get('completed_credits', 0),
                            enrollment_status='active',
                        )
                        profiles_to_create.append(profile)
                
                # 批量创建档案
                if len(profiles_to_create) >= self.batch_size:
                    StudentProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
                    profiles_to_create = []
                    self.log_progress(i + 1, total_users, "学生档案创建")
            
            # 创建剩余档案
            if profiles_to_create:
                StudentProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
                
        elif user_type == 'teacher':
            users = User.objects.filter(user_type='teacher').order_by('id')
            if limit:
                users = users[:limit]
            
            total_users = users.count()
            profiles_to_create = []
            
            user_list = list(users)
            for i, user in enumerate(user_list):
                if not TeacherProfile.objects.filter(user=user).exists():
                    profile = TeacherProfile(
                        user=user,
                        title=random.choice(['assistant', 'lecturer', 'associate_professor', 'professor']),
                        research_area=f"{user.department}相关研究",
                        office_location=f"{user.department}大楼{random.randint(100, 999)}室",
                        teaching_experience=random.randint(1, 20),
                        education_background='博士研究生',
                        is_active_teacher=True,
                    )
                    profiles_to_create.append(profile)
                
                # 批量创建档案
                if len(profiles_to_create) >= self.batch_size:
                    TeacherProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
                    profiles_to_create = []
                    self.log_progress(i + 1, total_users, "教师档案创建")
            
            # 创建剩余档案
            if profiles_to_create:
                TeacherProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)

def load_generated_data():
    """加载生成的JSON数据"""
    # Docker容器内的数据文件路径
    data_file = '/app/course_data.json'
    
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        print("ℹ️  请先将数据文件复制到容器中:")
        print(f"   docker cp <数据文件路径> course_management_backend:/app/course_data.json")
        return None
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 成功加载数据文件: {data_file}")
        print(f"📊 数据规模: 总计 {data['metadata']['total_records']:,} 条记录")
        return data
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return None

def create_departments(departments_data):
    """创建院系数据"""
    print("\n📚 处理院系数据...")
    dept_names = [dept['name'] for dept in departments_data]
    print(f"   ✅ 处理 {len(dept_names)} 个院系名称")
    return dept_names

def create_courses_batch(courses_data: List[Dict], dept_names: List[str], import_manager: DockerImportManager, limit: int = None):
    """批量创建课程（支持限制数量）"""
    print(f"\n📖 批量创建课程...")
    
    if limit:
        courses_data = courses_data[:limit]
    
    # 获取可用的教师
    teachers = list(User.objects.filter(user_type='teacher'))
    if not teachers:
        print("   ⚠️  未找到教师用户，跳过课程创建")
        return 0
    
    created_count = 0
    total_courses = len(courses_data)
    
    print(f"   📊 计划创建 {total_courses:,} 门课程...")
    
    for i in range(0, total_courses, import_manager.batch_size):
        batch = courses_data[i:i + import_manager.batch_size]
        
        try:
            with transaction.atomic():
                courses_to_create = []
                
                for course_data in batch:
                    try:
                        course_code = course_data['course_code']
                        if not Course.objects.filter(course_code=course_code).exists():
                            teacher = random.choice(teachers)
                            course = Course(
                                course_code=course_code,
                                name=course_data['name'],
                                description=course_data.get('description', ''),
                                credits=course_data.get('credits', 3),
                                capacity=course_data.get('capacity', 50),
                                teacher=teacher,
                                department=random.choice(dept_names) if dept_names else '未分配',
                                semester=course_data.get('semester', '2024-1'),
                                classroom=course_data.get('classroom', f"教室{random.randint(101, 999)}"),
                                schedule_time=course_data.get('schedule_time', '周一 09:00-11:00'),
                                is_active=course_data.get('is_active', True),
                            )
                            courses_to_create.append(course)
                    except Exception as e:
                        import_manager.error_count += 1
                        continue
                
                # 批量创建课程
                if courses_to_create:
                    Course.objects.bulk_create(courses_to_create, ignore_conflicts=True)
                    created_count += len(courses_to_create)
            
            # 记录进度
            import_manager.log_progress(min(i + import_manager.batch_size, total_courses), total_courses, "课程创建")
            
            # 定期垃圾回收
            if i % (import_manager.batch_size * 3) == 0:
                gc.collect()
                
        except Exception as e:
            print(f"   ❌ 批量创建课程失败: {e}")
            import_manager.error_count += len(batch)
            continue
    
    print(f"   ✅ 成功创建 {created_count:,} 门课程")
    return created_count

def create_enrollments_batch(enrollments_data: List[Dict], import_manager: DockerImportManager, limit: int = None):
    """批量创建选课记录（支持限制数量）"""
    print(f"\n📝 批量创建选课记录...")
    
    if limit:
        enrollments_data = enrollments_data[:limit]
    
    # 获取所有学生和课程
    students = {user.student_id: user for user in User.objects.filter(user_type='student')}
    courses = {course.course_code: course for course in Course.objects.all()}
    
    if not students or not courses:
        print("   ⚠️  未找到学生或课程，跳过选课记录创建")
        return 0
    
    created_count = 0
    total_enrollments = len(enrollments_data)
    
    print(f"   📊 计划创建 {total_enrollments:,} 条选课记录...")
    
    for i in range(0, total_enrollments, import_manager.batch_size):
        batch = enrollments_data[i:i + import_manager.batch_size]
        
        try:
            with transaction.atomic():
                enrollments_to_create = []
                
                for enrollment_data in batch:
                    try:
                        student_id = enrollment_data['student_id']
                        course_code = enrollment_data['course_code']
                        
                        student = students.get(student_id)
                        course = courses.get(course_code)
                        
                        if student and course:
                            if not Enrollment.objects.filter(student=student, course=course).exists():
                                enrollment = Enrollment(
                                    student=student,
                                    course=course,
                                    enrollment_date=timezone.now(),
                                    status='enrolled',
                                    grade=enrollment_data.get('grade', ''),
                                    attendance_rate=Decimal(str(enrollment_data.get('attendance_rate', 95.0))),
                                )
                                enrollments_to_create.append(enrollment)
                    except Exception as e:
                        import_manager.error_count += 1
                        continue
                
                # 批量创建选课记录
                if enrollments_to_create:
                    Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
                    created_count += len(enrollments_to_create)
            
            # 记录进度
            import_manager.log_progress(min(i + import_manager.batch_size, total_enrollments), total_enrollments, "选课记录创建")
            
            # 定期垃圾回收
            if i % (import_manager.batch_size * 2) == 0:
                gc.collect()
                
        except Exception as e:
            print(f"   ❌ 批量创建选课记录失败: {e}")
            import_manager.error_count += len(batch)
            continue
    
    print(f"   ✅ 成功创建 {created_count:,} 条选课记录")
    return created_count

def main():
    """主函数"""
    start_time = time.time()
    
    print("🚀 Docker环境百万级数据导入系统启动")
    print("=" * 80)
    
    # 加载数据
    data = load_generated_data()
    if not data:
        print("❌ 无法加载数据文件，退出程序")
        return
    
    # 初始化导入管理器（较小的批次大小适应Docker环境）
    import_manager = DockerImportManager(batch_size=2000)
    
    # 设置导入限制（可以根据需要调整）
    STUDENT_LIMIT = 100000  # 不限制，导入所有学生
    TEACHER_LIMIT = 5000    # 不限制，导入所有教师
    COURSE_LIMIT = 12000    # 不限制，导入所有课程
    ENROLLMENT_LIMIT = None # 不限制，导入所有选课记录
    
    try:
        # 开始导入
        print(f"\n🎬 开始百万级数据导入...")
        print(f"📊 数据规模: 总计 {data['metadata']['total_records']:,} 条记录")
        print(f"📊 导入限制: 学生 {STUDENT_LIMIT:,}, 教师 {TEACHER_LIMIT:,}, 课程 {COURSE_LIMIT:,}")
        
        # 处理院系数据
        dept_names = create_departments(data['departments'])
        
        # 批量创建学生用户
        students_count = import_manager.batch_create_users(
            data['students'], 'student', dept_names, STUDENT_LIMIT
        )
        
        # 批量创建教师用户
        teachers_count = import_manager.batch_create_users(
            data['teachers'], 'teacher', dept_names, TEACHER_LIMIT
        )
        
        # 创建用户档案
        import_manager.create_user_profiles('student', data['students'], data.get('majors', []), STUDENT_LIMIT)
        import_manager.create_user_profiles('teacher', data['teachers'], limit=TEACHER_LIMIT)
        
        # 批量创建课程
        courses_count = create_courses_batch(data['courses'], dept_names, import_manager, COURSE_LIMIT)
        
        # 批量创建选课记录
        enrollments_count = create_enrollments_batch(data.get('enrollments', []), import_manager, ENROLLMENT_LIMIT)
        
        # 计算总导入时间
        end_time = time.time()
        duration = end_time - start_time
        
        # 输出最终统计
        print("\n" + "=" * 80)
        print("🎉 百万级数据导入完成！")
        print("=" * 80)
        print(f"📊 导入统计:")
        print(f"   👥 学生用户: {students_count:,}")
        print(f"   👨‍🏫 教师用户: {teachers_count:,}")
        print(f"   📖 课程: {courses_count:,}")
        print(f"   📝 选课记录: {enrollments_count:,}")
        print(f"   📊 总记录数: {students_count + teachers_count + courses_count + enrollments_count:,}")
        print(f"   ⏱️  总用时: {duration:.2f} 秒")
        if duration > 0:
            print(f"   🚀 导入速度: {(students_count + teachers_count + courses_count + enrollments_count) / duration:.0f} 条/秒")
        print(f"   ❌ 错误数: {import_manager.error_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("✅ 百万级数据导入任务完成！")

if __name__ == "__main__":
    main()