#!/usr/bin/env python
"""
百万级数据导入脚本 - 增强版
支持大规模数据的高效导入，包含内存优化、分批处理和详细进度监控
提供实时进度条、内存监控、性能统计和状态反馈
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

# 导入进度监控系统
try:
    from progress_monitor import ImportProgressManager, create_progress_manager
    PROGRESS_MONITOR_AVAILABLE = True
except ImportError:
    print("⚠️ 进度监控模块未找到，将使用基础进度显示")
    PROGRESS_MONITOR_AVAILABLE = False

# 设置Django环境
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction, connection
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.courses.models import Course, Enrollment

User = get_user_model()

class MemoryOptimizer:
    """内存优化管理器"""
    
    def __init__(self, max_memory_gb=2):
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.current_usage = 0
        
    def monitor_memory(self):
        """监控内存使用情况"""
        process = psutil.Process()
        self.current_usage = process.memory_info().rss
        return self.current_usage / self.max_memory_bytes
    
    def force_garbage_collection(self):
        """强制垃圾回收"""
        gc.collect()
        
    def optimize_batch_size(self, current_batch_size):
        """动态调整批次大小"""
        memory_ratio = self.monitor_memory()
        if memory_ratio > 0.8:
            return max(1000, current_batch_size // 2)
        elif memory_ratio < 0.5:
            return min(50000, current_batch_size * 2)
        return current_batch_size

class BatchImportManager:
    """批量导入管理器，支持大规模数据分批处理和进度监控"""
    
    def __init__(self, batch_size=10000, max_memory_mb=1024):
        self.batch_size = batch_size
        self.max_memory_mb = max_memory_mb
        self.imported_count = 0
        self.error_count = 0
        self.memory_optimizer = MemoryOptimizer(max_memory_gb=max_memory_mb/1024)
        
        # 初始化进度管理器
        if PROGRESS_MONITOR_AVAILABLE:
            self.progress_manager = create_progress_manager(max_memory_gb=max_memory_mb/1024)
        else:
            self.progress_manager = None
        
        # 预计算密码哈希
        self.student_password_hash = make_password('student123')
        self.teacher_password_hash = make_password('teacher123')
        
    def log_progress(self, current, total, operation="导入"):
        """记录进度 - 增强版"""
        percentage = (current / total) * 100 if total > 0 else 0
        memory_usage = self.memory_optimizer.monitor_memory() * 100
        
        # 使用进度管理器更新进度
        if self.progress_manager:
            self.progress_manager.update_progress(operation, current, self.error_count)
        else:
            # 基础进度显示
            progress_bar = self._create_simple_progress_bar(percentage)
            print(f"\r   {progress_bar} {operation}进度: {current:,}/{total:,} ({percentage:.1f}%) | 内存使用: {memory_usage:.1f}%", end='', flush=True)
    
    def _create_simple_progress_bar(self, percentage: float, length: int = 30) -> str:
        """创建简单的文本进度条"""
        filled_length = int(length * percentage / 100)
        bar = '█' * filled_length + '░' * (length - filled_length)
        return f'[{bar}] {percentage:6.1f}%'
        
    def batch_create_users(self, users_data: List[Dict], user_type: str, dept_names: List[str]) -> int:
        """批量创建用户"""
        created_count = 0
        total_users = len(users_data)
        current_batch_size = self.batch_size
        
        print(f"\n👥 开始批量创建{user_type}用户...")
        print(f"   📊 计划创建 {total_users:,} 个{user_type}用户...")
        
        for i in range(0, total_users, current_batch_size):
            batch = users_data[i:i + current_batch_size]
            
            # 动态调整批次大小
            if self.progress_manager:
                current_batch_size = self.progress_manager.get_optimized_batch_size(current_batch_size)
            else:
                current_batch_size = self.memory_optimizer.optimize_batch_size(current_batch_size)
            
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
                            print(f"   ⚠️  处理{user_type} {user_data.get('name', 'Unknown')} 时出错: {e}")
                            continue
                    
                    # 批量创建用户
                    if batch_users:
                        User.objects.bulk_create(batch_users, ignore_conflicts=True)
                        created_count += len(batch_users)
                
                # 记录进度
                self.log_progress(min(i + current_batch_size, total_users), total_users, f"{user_type}用户创建")
                
                # 定期垃圾回收
                if i % (current_batch_size * 5) == 0:
                    self.memory_optimizer.force_garbage_collection()
                    
            except Exception as e:
                print(f"   ❌ 批量创建{user_type}用户失败: {e}")
                self.error_count += len(batch)
                continue
        
        print(f"   ✅ 成功创建 {created_count:,} 个{user_type}用户")
        return created_count
    
    def create_user_profiles(self, user_type: str, users_data: List[Dict], majors_data: List[Dict] = None):
        """创建用户档案"""
        print(f"\n📋 创建{user_type}档案...")
        
        if user_type == 'student':
            major_map = {major['id']: major['name'] for major in majors_data} if majors_data else {}
            users = User.objects.filter(user_type='student').order_by('id')
            total_users = users.count()
            
            profiles_to_create = []
            current_batch_size = self.batch_size
            
            for i, user in enumerate(users.iterator(chunk_size=current_batch_size)):
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
                if len(profiles_to_create) >= current_batch_size:
                    StudentProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
                    profiles_to_create = []
                    self.log_progress(i + 1, total_users, "学生档案创建")
                    
                    # 动态调整批次大小
                    current_batch_size = self.memory_optimizer.optimize_batch_size(current_batch_size)
            
            # 创建剩余档案
            if profiles_to_create:
                StudentProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
                
        elif user_type == 'teacher':
            users = User.objects.filter(user_type='teacher').order_by('id')
            total_users = users.count()
            
            profiles_to_create = []
            current_batch_size = self.batch_size
            
            for i, user in enumerate(users.iterator(chunk_size=current_batch_size)):
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
                if len(profiles_to_create) >= current_batch_size:
                    TeacherProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
                    profiles_to_create = []
                    self.log_progress(i + 1, total_users, "教师档案创建")
                    
                    # 动态调整批次大小
                    current_batch_size = self.memory_optimizer.optimize_batch_size(current_batch_size)
            
            # 创建剩余档案
            if profiles_to_create:
                TeacherProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)

def stream_json_data(file_path: str) -> Iterator[Dict[str, Any]]:
    """流式读取大型JSON文件"""
    print(f"📂 开始流式读取数据文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 成功加载数据文件，总计 {data['metadata']['total_records']:,} 条记录")
        return data
    except FileNotFoundError:
        print(f"❌ 数据文件不存在: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return None

def load_generated_data():
    """加载生成的JSON数据"""
    # 尝试多个可能的数据文件位置
    possible_paths = [
        '/app/course_data.json',
        'optimized_large_output/json/course_data.json',
        'conservative_large_output/json/course_data.json',
    ]
    
    for data_file in possible_paths:
        if os.path.exists(data_file):
            return stream_json_data(data_file)
    
    # 查找最新的数据文件
    data_dirs = [
        'optimized_large_output/json/',
        'conservative_large_output/json/',
        'data_output_large/json/',
        'data_output/json/'
    ]
    
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            json_files = list(Path(data_dir).glob('*.json'))
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                print(f"🔍 找到数据文件: {latest_file}")
                return stream_json_data(str(latest_file))
    
    print("❌ 未找到任何数据文件")
    return None

def create_departments(departments_data):
    """创建院系数据（作为用户的department字段）"""
    print("\n📚 处理院系数据...")
    
    # 提取院系名称供后续使用
    dept_names = [dept['name'] for dept in departments_data]
    print(f"   ✅ 处理 {len(dept_names)} 个院系名称")
    return dept_names

def create_courses_batch(courses_data: List[Dict], dept_names: List[str], import_manager: BatchImportManager):
    """批量创建课程"""
    print(f"\n📖 批量创建课程...")
    
    # 获取可用的教师
    teachers = list(User.objects.filter(user_type='teacher'))
    if not teachers:
        print("   ⚠️  未找到教师用户，跳过课程创建")
        return 0
    
    created_count = 0
    total_courses = len(courses_data)
    current_batch_size = import_manager.batch_size
    
    print(f"   📊 计划创建 {total_courses:,} 门课程...")
    
    for i in range(0, total_courses, current_batch_size):
        batch = courses_data[i:i + current_batch_size]
        
        # 动态调整批次大小
        current_batch_size = import_manager.memory_optimizer.optimize_batch_size(current_batch_size)
        
        try:
            with transaction.atomic():
                courses_to_create = []
                
                for course_data in batch:
                    try:
                        # 检查课程是否已存在
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
                        print(f"   ⚠️  处理课程 {course_data.get('name', 'Unknown')} 时出错: {e}")
                        continue
                
                # 批量创建课程
                if courses_to_create:
                    Course.objects.bulk_create(courses_to_create, ignore_conflicts=True)
                    created_count += len(courses_to_create)
            
            # 记录进度
            import_manager.log_progress(min(i + current_batch_size, total_courses), total_courses, "课程创建")
            
            # 定期垃圾回收
            if i % (current_batch_size * 3) == 0:
                import_manager.memory_optimizer.force_garbage_collection()
                
        except Exception as e:
            print(f"   ❌ 批量创建课程失败: {e}")
            import_manager.error_count += len(batch)
            continue
    
    print(f"   ✅ 成功创建 {created_count:,} 门课程")
    return created_count

def create_enrollments_batch(enrollments_data: List[Dict], import_manager: BatchImportManager):
    """批量创建选课记录"""
    print(f"\n📝 批量创建选课记录...")
    
    # 获取所有学生和课程
    students = {user.student_id: user for user in User.objects.filter(user_type='student')}
    courses = {course.course_code: course for course in Course.objects.all()}
    
    if not students or not courses:
        print("   ⚠️  未找到学生或课程，跳过选课记录创建")
        return 0
    
    created_count = 0
    total_enrollments = len(enrollments_data)
    current_batch_size = import_manager.batch_size
    
    print(f"   📊 计划创建 {total_enrollments:,} 条选课记录...")
    
    for i in range(0, total_enrollments, current_batch_size):
        batch = enrollments_data[i:i + current_batch_size]
        
        # 动态调整批次大小
        current_batch_size = import_manager.memory_optimizer.optimize_batch_size(current_batch_size)
        
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
                            # 检查选课记录是否已存在
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
            import_manager.log_progress(min(i + current_batch_size, total_enrollments), total_enrollments, "选课记录创建")
            
            # 定期垃圾回收
            if i % (current_batch_size * 2) == 0:
                import_manager.memory_optimizer.force_garbage_collection()
                
        except Exception as e:
            print(f"   ❌ 批量创建选课记录失败: {e}")
            import_manager.error_count += len(batch)
            continue
    
    print(f"   ✅ 成功创建 {created_count:,} 条选课记录")
    return created_count

def optimize_database_for_import():
    """优化数据库以加速导入"""
    print("\n⚡ 优化数据库设置...")
    
    with connection.cursor() as cursor:
        # 禁用自动提交
        cursor.execute("SET autocommit = OFF;")
        
        # 增加批量插入大小
        cursor.execute("SET SESSION bulk_insert_buffer_size = 256*1024*1024;")
        
        # 优化innodb设置（如果使用MySQL）
        try:
            cursor.execute("SET SESSION innodb_flush_log_at_trx_commit = 0;")
        except:
            pass
    
    print("   ✅ 数据库优化完成")

def restore_database_settings():
    """恢复数据库正常设置"""
    print("\n🔄 恢复数据库设置...")
    
    with connection.cursor() as cursor:
        # 恢复自动提交
        cursor.execute("SET autocommit = ON;")
        
        # 恢复正常设置
        try:
            cursor.execute("SET SESSION innodb_flush_log_at_trx_commit = 1;")
        except:
            pass
    
    print("   ✅ 数据库设置恢复完成")

def main():
    """主函数"""
    start_time = time.time()
    
    print("🚀 百万级数据导入系统启动")
    print("=" * 80)
    
    # 加载数据
    data = load_generated_data()
    if not data:
        print("❌ 无法加载数据文件，退出程序")
        return
    
    # 初始化导入管理器
    import_manager = BatchImportManager(batch_size=5000, max_memory_mb=2048)
    
    try:
        # 启动进度监控系统
        if import_manager.progress_manager:
            import_manager.progress_manager.start_monitoring()
            print("🚀 进度监控系统已启动")
        
        # 优化数据库
        optimize_database_for_import()
        
        # 开始导入
        print(f"\n🎬 开始百万级数据导入...")
        print(f"📊 数据规模: 总计 {data['metadata']['total_records']:,} 条记录")
        
        # 处理院系数据
        dept_names = create_departments(data['departments'])
        
        # 批量创建学生用户
        students_count = import_manager.batch_create_users(
            data['students'], 'student', dept_names
        )
        
        # 批量创建教师用户
        teachers_count = import_manager.batch_create_users(
            data['teachers'], 'teacher', dept_names
        )
        
        # 创建用户档案
        import_manager.create_user_profiles('student', data['students'], data.get('majors', []))
        import_manager.create_user_profiles('teacher', data['teachers'])
        
        # 批量创建课程
        courses_count = create_courses_batch(data['courses'], dept_names, import_manager)
        
        # 批量创建选课记录
        enrollments_count = create_enrollments_batch(data.get('enrollments', []), import_manager)
        
        # 计算总导入时间
        end_time = time.time()
        duration = end_time - start_time
        
        # 恢复数据库设置
        restore_database_settings()
        
        # 停止进度监控系统
        if import_manager.progress_manager:
            import_manager.progress_manager.stop_monitoring()
        
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
        print(f"   🚀 导入速度: {(students_count + teachers_count + courses_count + enrollments_count) / duration:.0f} 条/秒")
        print(f"   ❌ 错误数: {import_manager.error_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        restore_database_settings()
        
        # 停止进度监控系统
        if import_manager.progress_manager:
            import_manager.progress_manager.stop_monitoring()
        return
    
    print("✅ 百万级数据导入任务完成！")

if __name__ == "__main__":
    main()