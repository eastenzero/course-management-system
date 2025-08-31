"""
Django管理命令：导入大规模测试数据
"""

import json
import os
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings

from apps.courses.models import Course, Enrollment
from apps.students.models import Profile as StudentProfile
from apps.teachers.models import Profile as TeacherProfile

User = get_user_model()


class Command(BaseCommand):
    help = '导入大规模测试数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-file',
            type=str,
            help='JSON数据文件路径',
            default='../data-generator/conservative_large_output/json/course_data_20250830_161558.json'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='批处理大小'
        )

    def handle(self, *args, **options):
        data_file = options['data_file']
        batch_size = options['batch_size']

        self.stdout.write(self.style.SUCCESS('🚀 开始大规模数据导入'))
        self.stdout.write('='*80)

        try:
            # 加载JSON数据
            data = self.load_json_data(data_file)
            
            # 导入数据
            self.import_users_and_profiles(data['students'], data['teachers'], batch_size)
            self.import_courses(data['courses'], batch_size)
            self.import_enrollments(data['enrollments'], batch_size)
            
            self.show_final_statistics()
            
            self.stdout.write(self.style.SUCCESS('🎉 数据导入完成！'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 数据导入失败: {e}'))
            raise

    def load_json_data(self, file_path):
        """加载JSON数据文件"""
        self.stdout.write(f'📂 加载数据文件: {file_path}')
        
        full_path = Path(file_path)
        if not full_path.exists():
            # 尝试相对于backend目录的路径
            backend_dir = Path(__file__).parent.parent.parent
            full_path = backend_dir / file_path
            
        if not full_path.exists():
            raise FileNotFoundError(f'数据文件不存在: {file_path}')
        
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stdout.write(self.style.SUCCESS('✅ 数据文件加载成功'))
        self.stdout.write('📊 数据统计:')
        for key, value in data.items():
            if isinstance(value, list):
                self.stdout.write(f'   {key}: {len(value):,} 条记录')
        
        return data

    def import_users_and_profiles(self, students_data, teachers_data, batch_size):
        """导入用户和档案数据"""
        self.stdout.write('\n👥 开始导入用户数据...')
        
        # 准备用户数据
        users_to_create = []
        
        self.stdout.write('   📝 准备学生用户数据...')
        for student in students_data:
            user = User(
                username=student['username'],
                email=student['email'],
                first_name=student['first_name'],
                last_name=student['last_name'],
                user_type='student',
                is_active=True
            )
            user.set_password('password123')
            users_to_create.append(user)
        
        self.stdout.write('   📝 准备教师用户数据...')
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
        
        # 批量创建用户
        self.stdout.write(f'   💾 批量创建 {len(users_to_create):,} 个用户...')
        with transaction.atomic():
            User.objects.bulk_create(users_to_create, batch_size=batch_size, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('   ✅ 用户创建完成'))
        
        # 创建档案
        self.create_profiles(students_data, teachers_data, batch_size)

    def create_profiles(self, students_data, teachers_data, batch_size):
        """创建用户档案"""
        self.stdout.write('   📋 创建学生档案...')
        
        # 获取用户映射
        student_usernames = [s['username'] for s in students_data]
        student_users = {u.username: u for u in User.objects.filter(username__in=student_usernames)}
        
        student_profiles = []
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
                student_profiles.append(profile)
        
        # 创建教师档案
        self.stdout.write('   📋 创建教师档案...')
        teacher_usernames = [t['username'] for t in teachers_data]
        teacher_users = {u.username: u for u in User.objects.filter(username__in=teacher_usernames)}
        
        teacher_profiles = []
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
                teacher_profiles.append(profile)
        
        # 批量创建档案
        with transaction.atomic():
            StudentProfile.objects.bulk_create(student_profiles, batch_size=batch_size, ignore_conflicts=True)
            TeacherProfile.objects.bulk_create(teacher_profiles, batch_size=batch_size, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ 档案创建完成: {len(student_profiles):,} 学生档案, {len(teacher_profiles):,} 教师档案'
        ))

    def import_courses(self, courses_data, batch_size):
        """导入课程数据"""
        self.stdout.write('\n📚 开始导入课程数据...')
        
        courses_to_create = []
        for course in courses_data:
            course_obj = Course(
                name=course['name'],
                code=course['code'],
                credits=course.get('credits', 3),
                description=course.get('description', ''),
                course_type=course.get('type', 'elective'),
                max_students=course.get('max_students', 100),
                semester=course.get('semester', '2024-1'),
                is_active=True
            )
            courses_to_create.append(course_obj)
        
        with transaction.atomic():
            Course.objects.bulk_create(courses_to_create, batch_size=batch_size, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ 课程创建完成: {len(courses_to_create):,} 门课程'))

    def import_enrollments(self, enrollments_data, batch_size):
        """导入选课记录"""
        self.stdout.write('\n🎯 开始导入选课记录...')
        
        # 构建映射
        self.stdout.write('   📋 构建用户和课程映射...')
        users_map = {u.id: u for u in User.objects.filter(user_type='student')}
        courses_map = {c.id: c for c in Course.objects.all()}
        
        enrollments_to_create = []
        valid_count = 0
        batch_count = 0
        
        self.stdout.write('   🔍 处理选课记录...')
        for i, enrollment in enumerate(enrollments_data):
            if i % 20000 == 0 and i > 0:
                progress = (i / len(enrollments_data)) * 100
                self.stdout.write(f'      进度: {i:,}/{len(enrollments_data):,} ({progress:.1f}%)')
            
            student_id = enrollment.get('student_id')
            course_id = enrollment.get('course_id')
            
            if student_id in users_map and course_id in courses_map:
                enrollment_obj = Enrollment(
                    student=users_map[student_id],
                    course=courses_map[course_id],
                    enrollment_date=datetime.now().date(),
                    status='enrolled'
                )
                enrollments_to_create.append(enrollment_obj)
                valid_count += 1
                
                # 分批处理
                if len(enrollments_to_create) >= batch_size:
                    with transaction.atomic():
                        Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
                    enrollments_to_create = []
                    batch_count += 1
                    if batch_count % 10 == 0:
                        self.stdout.write(f'      已处理 {batch_count * batch_size:,} 条记录')
        
        # 处理剩余记录
        if enrollments_to_create:
            with transaction.atomic():
                Enrollment.objects.bulk_create(enrollments_to_create, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ 选课记录导入完成: {valid_count:,} 条有效记录'))

    def show_final_statistics(self):
        """显示最终统计信息"""
        self.stdout.write('\n📊 导入统计:')
        self.stdout.write(f'   用户总数: {User.objects.count():,}')
        self.stdout.write(f'   学生档案: {StudentProfile.objects.count():,}')
        self.stdout.write(f'   教师档案: {TeacherProfile.objects.count():,}')
        self.stdout.write(f'   课程总数: {Course.objects.count():,}')
        self.stdout.write(f'   选课记录: {Enrollment.objects.count():,}')