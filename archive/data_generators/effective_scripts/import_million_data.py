#!/usr/bin/env python3
"""
百万级数据导入脚本 - 优化版本
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any

# 添加backend到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')

try:
    import django
    django.setup()
    print("✅ Django环境初始化成功")
except Exception as e:
    print(f"❌ Django环境初始化失败: {e}")
    sys.exit(1)

# 导入Django模型
from django.contrib.auth import get_user_model
from django.db import transaction, connection, IntegrityError
from django.utils import timezone

try:
    from apps.courses.models import Course, Enrollment
    from apps.students.models import Profile as StudentProfile
    from apps.teachers.models import Profile as TeacherProfile
    from apps.classrooms.models import Classroom
    print("✅ Django模型导入成功")
except ImportError as e:
    print(f"❌ Django模型导入失败: {e}")
    sys.exit(1)

User = get_user_model()


class MillionDataImporter:
    """百万级数据导入器"""
    
    def __init__(self, data_file: str, batch_size: int = 5000):
        self.data_file = data_file
        self.batch_size = batch_size
        self.stats = {
            'imported': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        print(f"📂 加载数据文件: {self.data_file}")
        
        if not Path(self.data_file).exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ 数据文件加载成功")
            print(f"📊 数据统计:")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value):,} 条记录")
            
            return data
        except Exception as e:
            print(f"❌ 数据文件加载失败: {e}")
            raise
    
    def clear_existing_data(self):
        """清理现有数据（可选）"""
        print("\n🧹 清理现有数据...")
        
        try:
            with transaction.atomic():
                # 注意：按照外键依赖关系的顺序删除
                Enrollment.objects.all().delete()
                Course.objects.all().delete()
                StudentProfile.objects.all().delete()
                TeacherProfile.objects.all().delete()
                Classroom.objects.all().delete()
                User.objects.filter(is_superuser=False).delete()
                
            print("✅ 现有数据清理完成")
        except Exception as e:
            print(f"❌ 数据清理失败: {e}")
            raise
    
    def import_teachers(self, teachers_data: List[Dict]) -> Dict[str, Any]:
        """导入教师数据"""
        print(f"\n👨‍🏫 导入教师数据 ({len(teachers_data):,} 条)...")
        
        users_to_create = []
        profiles_to_create = []
        teacher_mapping = {}  # teacher_id -> User对象
        
        # 准备用户数据
        for i, teacher in enumerate(teachers_data):
            if i % 10000 == 0 and i > 0:
                print(f"   准备进度: {i:,}/{len(teachers_data):,}")
            
            username = f"teacher_{teacher['teacher_id']}"
            user = User(
                username=username,
                email=teacher.get('email', f"{username}@university.edu"),
                first_name=teacher['name'].split(' ')[0] if ' ' in teacher['name'] else teacher['name'],
                last_name=teacher['name'].split(' ', 1)[1] if ' ' in teacher['name'] else '',
                user_type='teacher',
                is_active=True
            )
            user.set_password('teacher123')
            users_to_create.append(user)
        
        # 批量创建用户
        print(f"   💾 批量创建 {len(users_to_create):,} 个教师用户...")
        try:
            with transaction.atomic():
                User.objects.bulk_create(users_to_create, batch_size=self.batch_size, ignore_conflicts=True)
            print(f"   ✅ 教师用户创建完成")
        except Exception as e:
            print(f"   ❌ 教师用户创建失败: {e}")
            raise
        
        # 获取创建的用户
        usernames = [f"teacher_{t['teacher_id']}" for t in teachers_data]
        created_users = {u.username: u for u in User.objects.filter(username__in=usernames)}
        
        # 准备教师档案数据
        for teacher in teachers_data:
            username = f"teacher_{teacher['teacher_id']}"
            if username in created_users:
                user = created_users[username]
                teacher_mapping[teacher['teacher_id']] = user
                
                profile = TeacherProfile(
                    user=user,
                    employee_id=teacher['teacher_id'],
                    department_name=teacher.get('department', '未指定院系'),
                    title=teacher.get('title', '讲师'),
                    phone=teacher.get('phone', ''),
                    office=f"Office-{teacher['teacher_id']}"
                )
                profiles_to_create.append(profile)
        
        # 批量创建教师档案
        print(f"   📋 批量创建 {len(profiles_to_create):,} 个教师档案...")
        try:
            with transaction.atomic():
                TeacherProfile.objects.bulk_create(profiles_to_create, batch_size=self.batch_size, ignore_conflicts=True)
            print(f"   ✅ 教师档案创建完成")
        except Exception as e:
            print(f"   ❌ 教师档案创建失败: {e}")
            raise
        
        return teacher_mapping
    
    def import_students(self, students_data: List[Dict]) -> Dict[str, Any]:
        """导入学生数据"""
        print(f"\n👨‍🎓 导入学生数据 ({len(students_data):,} 条)...")
        
        users_to_create = []
        profiles_to_create = []
        student_mapping = {}  # student_id -> User对象
        
        # 准备用户数据
        for i, student in enumerate(students_data):
            if i % 10000 == 0 and i > 0:
                print(f"   准备进度: {i:,}/{len(students_data):,}")
            
            username = f"student_{student['student_id']}"
            user = User(
                username=username,
                email=student.get('email', f"{username}@university.edu"),
                first_name=student['name'].split(' ')[0] if ' ' in student['name'] else student['name'],
                last_name=student['name'].split(' ', 1)[1] if ' ' in student['name'] else '',
                user_type='student',
                is_active=True
            )
            user.set_password('student123')
            users_to_create.append(user)
        
        # 批量创建用户
        print(f"   💾 批量创建 {len(users_to_create):,} 个学生用户...")
        try:
            with transaction.atomic():
                User.objects.bulk_create(users_to_create, batch_size=self.batch_size, ignore_conflicts=True)
            print(f"   ✅ 学生用户创建完成")
        except Exception as e:
            print(f"   ❌ 学生用户创建失败: {e}")
            raise
        
        # 获取创建的用户
        usernames = [f"student_{s['student_id']}" for s in students_data]
        created_users = {u.username: u for u in User.objects.filter(username__in=usernames)}
        
        # 准备学生档案数据
        for student in students_data:
            username = f"student_{student['student_id']}"
            if username in created_users:
                user = created_users[username]
                student_mapping[student['student_id']] = user
                
                profile = StudentProfile(
                    user=user,
                    student_id=student['student_id'],
                    major_name=student.get('major', '未指定专业'),
                    year=student.get('grade', 1),
                    phone=student.get('phone', ''),
                    address=f"Address-{student['student_id']}"
                )
                profiles_to_create.append(profile)
        
        # 批量创建学生档案
        print(f"   📋 批量创建 {len(profiles_to_create):,} 个学生档案...")
        try:
            with transaction.atomic():
                StudentProfile.objects.bulk_create(profiles_to_create, batch_size=self.batch_size, ignore_conflicts=True)
            print(f"   ✅ 学生档案创建完成")
        except Exception as e:
            print(f"   ❌ 学生档案创建失败: {e}")
            raise
        
        return student_mapping
    
    def import_classrooms(self, classrooms_data: List[Dict]):
        """导入教室数据"""
        print(f"\n🏫 导入教室数据 ({len(classrooms_data):,} 条)...")
        
        classrooms_to_create = []
        
        for classroom in classrooms_data:
            classroom_obj = Classroom(
                name=classroom.get('room_number', classroom['room_id']),
                building=classroom.get('building', 'A'),
                capacity=classroom.get('capacity', 50),
                room_type=classroom.get('room_type', '普通教室'),
                equipment=','.join(classroom.get('equipment', [])),
                is_available=classroom.get('is_available', True)
            )
            classrooms_to_create.append(classroom_obj)
        
        try:
            with transaction.atomic():
                Classroom.objects.bulk_create(classrooms_to_create, batch_size=self.batch_size, ignore_conflicts=True)
            print(f"   ✅ 教室创建完成: {len(classrooms_to_create):,} 间教室")
        except Exception as e:
            print(f"   ❌ 教室创建失败: {e}")
            raise
    
    def import_courses(self, courses_data: List[Dict], teacher_mapping: Dict[str, Any]):
        """导入课程数据"""
        print(f"\n📚 导入课程数据 ({len(courses_data):,} 条)...")
        
        courses_to_create = []
        course_mapping = {}  # course_id -> Course对象
        
        for course in courses_data:
            # 查找教师
            teacher_user = teacher_mapping.get(course.get('teacher_id'))
            
            course_obj = Course(
                name=course['name'],
                code=course.get('code', course['course_id']),
                credits=course.get('credits', 3),
                description=course.get('description', ''),
                course_type=course.get('type', 'elective'),
                teacher=teacher_user,
                max_students=course.get('student_capacity', 100),
                semester=course.get('semester', '2024-1'),
                is_active=True
            )
            courses_to_create.append(course_obj)
        
        try:
            with transaction.atomic():
                Course.objects.bulk_create(courses_to_create, batch_size=self.batch_size, ignore_conflicts=True)
            print(f"   ✅ 课程创建完成: {len(courses_to_create):,} 门课程")
        except Exception as e:
            print(f"   ❌ 课程创建失败: {e}")
            raise
        
        # 建立course_id到Course对象的映射
        created_courses = Course.objects.all()
        for i, course in enumerate(courses_data):
            if i < len(created_courses):
                course_mapping[course['course_id']] = created_courses[i]
        
        return course_mapping
    
    def import_enrollments(self, enrollments_data: List[Dict], 
                         student_mapping: Dict[str, Any], 
                         course_mapping: Dict[str, Any]):
        """导入选课记录"""
        print(f"\n🎯 导入选课记录 ({len(enrollments_data):,} 条)...")
        
        enrollments_to_create = []
        valid_count = 0
        
        print(f"   🔍 处理选课记录...")
        for i, enrollment in enumerate(enrollments_data):
            if i % 50000 == 0 and i > 0:
                print(f"      进度: {i:,}/{len(enrollments_data):,} ({i/len(enrollments_data)*100:.1f}%)")
            
            student_id = enrollment.get('student_id')
            course_id = enrollment.get('course_id')
            
            student_user = student_mapping.get(student_id)
            course_obj = course_mapping.get(course_id)
            
            if student_user and course_obj:
                enrollment_obj = Enrollment(
                    student=student_user,
                    course=course_obj,
                    semester=enrollment.get('semester', '2024-1'),
                    status=enrollment.get('status', '已选课'),
                    enrollment_date=timezone.now(),
                    grade=enrollment.get('grade')
                )
                enrollments_to_create.append(enrollment_obj)
                valid_count += 1
                
                # 分批创建以避免内存问题
                if len(enrollments_to_create) >= self.batch_size:
                    try:
                        with transaction.atomic():
                            Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
                        enrollments_to_create = []
                    except Exception as e:
                        print(f"   ⚠️ 批次导入失败: {e}")
                        enrollments_to_create = []
        
        # 导入剩余的记录
        if enrollments_to_create:
            try:
                with transaction.atomic():
                    Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
            except Exception as e:
                print(f"   ⚠️ 最后批次导入失败: {e}")
        
        print(f"   ✅ 选课记录创建完成: {valid_count:,} 条有效记录")
    
    def run_import(self, clear_existing: bool = False):
        """执行完整的数据导入流程"""
        print("🚀 开始百万级数据导入流程")
        print("=" * 60)
        
        self.stats['start_time'] = time.time()
        
        try:
            # 加载数据
            data = self.load_data()
            
            # 清理现有数据（可选）
            if clear_existing:
                self.clear_existing_data()
            
            # 导入基础数据
            teacher_mapping = self.import_teachers(data.get('teachers', []))
            student_mapping = self.import_students(data.get('students', []))
            self.import_classrooms(data.get('classrooms', []))
            course_mapping = self.import_courses(data.get('courses', []), teacher_mapping)
            
            # 导入关联数据
            self.import_enrollments(data.get('enrollments', []), student_mapping, course_mapping)
            
            self.stats['end_time'] = time.time()
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ 导入过程发生错误: {e}")
            raise
    
    def print_summary(self):
        """打印导入总结"""
        total_time = self.stats['end_time'] - self.stats['start_time']
        
        print(f"\n🎉 数据导入完成！")
        print(f"⏱️  总耗时: {total_time:.2f} 秒")
        print(f"📊 导入统计:")
        
        # 获取各表的记录数
        print(f"   用户: {User.objects.count():,}")
        print(f"   教师档案: {TeacherProfile.objects.count():,}")
        print(f"   学生档案: {StudentProfile.objects.count():,}")
        print(f"   课程: {Course.objects.count():,}")
        print(f"   教室: {Classroom.objects.count():,}")
        print(f"   选课记录: {Enrollment.objects.count():,}")
        
        total_records = (User.objects.count() + TeacherProfile.objects.count() + 
                        StudentProfile.objects.count() + Course.objects.count() + 
                        Classroom.objects.count() + Enrollment.objects.count())
        
        print(f"   总记录数: {total_records:,}")
        if total_time > 0:
            print(f"   导入速度: {total_records/total_time:.0f} 条/秒")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='百万级数据导入器')
    parser.add_argument('--data-file', default='course_data_output/course_dataset.json', 
                       help='数据文件路径')
    parser.add_argument('--batch-size', type=int, default=5000, 
                       help='批次大小')
    parser.add_argument('--clear', action='store_true', 
                       help='清理现有数据')
    
    args = parser.parse_args()
    
    importer = MillionDataImporter(args.data_file, args.batch_size)
    importer.run_import(clear_existing=args.clear)


if __name__ == "__main__":
    main()