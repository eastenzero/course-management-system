"""
Django管理命令：导入生成的测试数据
功能：将data-generator生成的JSON数据导入到Django数据库中
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, timezone
from django.utils import timezone as django_timezone

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.courses.models import Course, Enrollment
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import TimeSlot

User = get_user_model()


class Command(BaseCommand):
    """数据导入管理命令"""
    
    help = '导入生成的测试数据到数据库'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--file',
            type=str,
            help='指定要导入的JSON文件路径'
        )
        parser.add_argument(
            '--auto-discover',
            action='store_true',
            help='自动发现并使用推荐的数据文件'
        )
        parser.add_argument(
            '--clear-data',
            action='store_true',
            help='导入前清除现有数据'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='批量导入的记录数量 (默认: 1000)'
        )
        parser.add_argument(
            '--skip-validation',
            action='store_true',
            help='跳过数据验证（提高导入速度）'
        )
    
    def handle(self, *args, **options):
        """命令主入口"""
        self.stdout.write("🚀 开始导入测试数据...")
        self.stdout.write("=" * 60)
        
        try:
            # 获取数据文件路径
            data_file_path = self._get_data_file_path(options)
            
            # 验证文件存在
            if not Path(data_file_path).exists():
                raise CommandError(f"数据文件不存在: {data_file_path}")
            
            self.stdout.write(f"📁 数据文件: {data_file_path}")
            
            # 加载JSON数据
            self.stdout.write("📖 加载数据文件...")
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 显示数据统计
            self._show_data_statistics(data)
            
            # 清除现有数据（如果需要）
            if options['clear_data']:
                self._clear_existing_data()
            
            # 执行数据导入
            with transaction.atomic():
                import_stats = self._import_data(data, options)
            
            # 显示导入结果
            self._show_import_results(import_stats)
            
            # 验证导入数据
            if not options['skip_validation']:
                self._validate_imported_data()
            
            self.stdout.write("🎉 数据导入完成！")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ 导入失败: {str(e)}")
            )
            raise CommandError(f"数据导入失败: {str(e)}")
    
    def _get_data_file_path(self, options: Dict) -> str:
        """获取数据文件路径"""
        if options['file']:
            return options['file']
        
        if options['auto_discover']:
            # 读取推荐文件路径
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            recommended_file = base_dir / '.recommended_data_file'
            
            if recommended_file.exists():
                with open(recommended_file, 'r') as f:
                    return f.read().strip()
            else:
                raise CommandError("未找到推荐的数据文件，请先运行数据发现脚本")
        
        raise CommandError("请指定数据文件路径 (--file) 或使用自动发现 (--auto-discover)")
    
    def _show_data_statistics(self, data: Dict[str, Any]) -> None:
        """显示数据统计信息"""
        self.stdout.write("\n📊 数据统计:")
        self.stdout.write("-" * 40)
        
        total_records = 0
        for key, value in data.items():
            if isinstance(value, list) and key != 'metadata':
                count = len(value)
                total_records += count
                self.stdout.write(f"  📋 {key}: {count:,} 条")
        
        self.stdout.write(f"  📈 总计: {total_records:,} 条记录")
        
        # 显示元数据
        if 'metadata' in data:
            metadata = data['metadata']
            self.stdout.write(f"\n📝 数据集信息:")
            self.stdout.write(f"  🏷️  规模: {metadata.get('scale', 'unknown')}")
            self.stdout.write(f"  📅 生成时间: {metadata.get('generated_at', 'unknown')}")
            self.stdout.write(f"  ✅ 验证状态: {'通过' if metadata.get('validation_passed', False) else '未通过'}")
    
    def _clear_existing_data(self) -> None:
        """清除现有数据"""
        self.stdout.write("\n🗑️  清除现有数据...")
        
        # 按照外键依赖顺序删除
        models_to_clear = [
            Enrollment,      # 选课记录
            Course,          # 课程
            StudentProfile,  # 学生档案
            TeacherProfile,  # 教师档案
            User,           # 用户（除了超级用户）
            TimeSlot,       # 时间段
            Classroom,      # 教室
            Building,       # 建筑
        ]
        
        for model in models_to_clear:
            if model == User:
                # 保留超级用户
                count = model.objects.filter(is_superuser=False).count()
                model.objects.filter(is_superuser=False).delete()
            else:
                count = model.objects.count()
                model.objects.all().delete()
            
            self.stdout.write(f"   ✅ 清除 {model._meta.verbose_name}: {count} 条")
    
    def _import_data(self, data: Dict[str, Any], options: Dict) -> Dict[str, int]:
        """执行数据导入"""
        self.stdout.write("\n💾 开始导入数据...")
        batch_size = options['batch_size']
        import_stats = {}
        
        # 按照依赖顺序导入数据
        import_order = [
            ('departments', self._import_departments),
            ('majors', self._import_majors),  
            ('buildings', self._import_buildings),
            ('classrooms', self._import_classrooms),
            ('time_slots', self._import_time_slots),
            ('students', self._import_students),
            ('teachers', self._import_teachers),
            ('courses', self._import_courses),
            ('enrollments', self._import_enrollments),
        ]
        
        for data_key, import_func in import_order:
            if data_key in data and data[data_key]:
                self.stdout.write(f"\n📥 导入 {data_key}...")
                count = import_func(data[data_key], batch_size)
                import_stats[data_key] = count
                self.stdout.write(f"   ✅ 成功导入: {count} 条")
        
        return import_stats
    
    def _import_departments(self, departments: List[Dict], batch_size: int) -> int:
        """导入院系数据 - 创建为Building对象"""
        buildings_to_create = []
        
        for dept_data in departments:
            building = Building(
                name=dept_data['name'],
                code=dept_data['code'],
                address=dept_data.get('office_address', ''),
                description=dept_data.get('description', ''),
                floors=3,  # 默认3层
                is_active=dept_data.get('is_active', True)
            )
            buildings_to_create.append(building)
        
        Building.objects.bulk_create(buildings_to_create, batch_size=batch_size)
        return len(buildings_to_create)
    
    def _import_majors(self, majors: List[Dict], batch_size: int) -> int:
        """导入专业数据 - 暂时跳过，因为没有对应的模型"""
        # TODO: 如果需要专业模型，可以在这里实现
        self.stdout.write("   ⚠️  专业数据暂时跳过（无对应模型）")
        return 0
    
    def _import_buildings(self, buildings: List[Dict], batch_size: int) -> int:
        """导入建筑数据"""
        # 已在departments中处理
        return 0
    
    def _import_classrooms(self, classrooms: List[Dict], batch_size: int) -> int:
        """导入教室数据"""
        # 确保有默认建筑
        default_building, created = Building.objects.get_or_create(
            code='DEFAULT',
            defaults={
                'name': '默认教学楼',
                'address': '校园内',
                'floors': 5,
                'is_active': True
            }
        )
        
        classrooms_to_create = []
        for classroom_data in classrooms:
            classroom = Classroom(
                building=default_building,
                room_number=classroom_data['room_number'],
                name=classroom_data.get('name', f"教室{classroom_data['room_number']}"),
                capacity=classroom_data.get('capacity', 50),
                classroom_type=classroom_data.get('room_type', 'lecture'),
                floor=classroom_data.get('floor', 1),
                equipment=', '.join(classroom_data.get('equipment', [])),
                is_active=classroom_data.get('is_active', True)
            )
            classrooms_to_create.append(classroom)
        
        Classroom.objects.bulk_create(classrooms_to_create, batch_size=batch_size)
        return len(classrooms_to_create)
    
    def _import_time_slots(self, time_slots: List[Dict], batch_size: int) -> int:
        """导入时间段数据"""
        time_slots_to_create = []
        
        for slot_data in time_slots:
            # 解析时间字符串
            start_time = datetime.strptime(slot_data['start_time'], '%H:%M:%S').time()
            end_time = datetime.strptime(slot_data['end_time'], '%H:%M:%S').time()
            
            time_slot = TimeSlot(
                name=slot_data['name'],
                start_time=start_time,
                end_time=end_time,
                day_of_week=slot_data.get('day_of_week', 1),
                is_active=slot_data.get('is_active', True)
            )
            time_slots_to_create.append(time_slot)
        
        TimeSlot.objects.bulk_create(time_slots_to_create, batch_size=batch_size)
        return len(time_slots_to_create)
    
    def _import_students(self, students: List[Dict], batch_size: int) -> int:
        """导入学生数据"""
        users_to_create = []
        profiles_to_create = []
        
        # 批量创建用户
        for student_data in students:
            user = User(
                username=student_data['username'],
                email=student_data['email'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                user_type='student',
                student_id=student_data['student_id'],
                department=student_data.get('department', ''),
                phone=student_data.get('phone', ''),
                is_active=student_data.get('is_active', True)
            )
            users_to_create.append(user)
        
        # 批量创建用户
        User.objects.bulk_create(users_to_create, batch_size=batch_size)
        
        # 获取创建的用户
        created_users = User.objects.filter(
            username__in=[s['username'] for s in students]
        )
        user_map = {user.username: user for user in created_users}
        
        # 创建学生档案
        for student_data in students:
            username = student_data['username']
            if username in user_map:
                profile = StudentProfile(
                    user=user_map[username],
                    admission_year=student_data.get('admission_year', 2024),
                    major=student_data.get('major', ''),
                    class_name=student_data.get('class_name', ''),
                    gpa=Decimal(str(student_data.get('gpa', 0.0))),
                    total_credits=student_data.get('total_credits', 0),
                    completed_credits=student_data.get('completed_credits', 0),
                    enrollment_status=student_data.get('enrollment_status', 'enrolled')
                )
                profiles_to_create.append(profile)
        
        StudentProfile.objects.bulk_create(profiles_to_create, batch_size=batch_size)
        return len(users_to_create)
    
    def _import_teachers(self, teachers: List[Dict], batch_size: int) -> int:
        """导入教师数据"""
        users_to_create = []
        profiles_to_create = []
        
        # 批量创建用户
        for teacher_data in teachers:
            user = User(
                username=teacher_data['username'],
                email=teacher_data['email'],
                first_name=teacher_data['first_name'],
                last_name=teacher_data['last_name'],
                user_type='teacher',
                employee_id=teacher_data['employee_id'],
                department=teacher_data.get('department', ''),
                phone=teacher_data.get('phone', ''),
                is_active=teacher_data.get('is_active', True)
            )
            users_to_create.append(user)
        
        # 批量创建用户
        User.objects.bulk_create(users_to_create, batch_size=batch_size)
        
        # 获取创建的用户
        created_users = User.objects.filter(
            username__in=[t['username'] for t in teachers]
        )
        user_map = {user.username: user for user in created_users}
        
        # 创建教师档案
        for teacher_data in teachers:
            username = teacher_data['username']
            if username in user_map:
                profile = TeacherProfile(
                    user=user_map[username],
                    title=teacher_data.get('title', 'lecturer'),
                    research_area=teacher_data.get('research_area', ''),
                    office_location=teacher_data.get('office_location', ''),
                    teaching_experience=teacher_data.get('teaching_experience', 0),
                    education_background=teacher_data.get('education_background', ''),
                    is_active_teacher=teacher_data.get('is_active_teacher', True)
                )
                profiles_to_create.append(profile)
        
        TeacherProfile.objects.bulk_create(profiles_to_create, batch_size=batch_size)
        return len(users_to_create)
    
    def _import_courses(self, courses: List[Dict], batch_size: int) -> int:
        """导入课程数据"""
        courses_to_create = []
        
        for course_data in courses:
            course = Course(
                code=course_data['code'],
                name=course_data['name'],
                english_name=course_data.get('english_name', ''),
                course_type=course_data.get('course_type', 'required'),
                credits=course_data.get('credits', 3),
                hours=course_data.get('hours', 48),
                department=course_data.get('department', ''),
                semester=course_data.get('semester', '2024-1'),
                academic_year=course_data.get('academic_year', '2024'),
                description=course_data.get('description', ''),
                objectives=course_data.get('objectives', ''),
                max_students=course_data.get('max_students', 50),
                min_students=course_data.get('min_students', 10),
                is_active=course_data.get('is_active', True),
                is_published=course_data.get('is_published', True)
            )
            courses_to_create.append(course)
        
        Course.objects.bulk_create(courses_to_create, batch_size=batch_size)
        
        # 处理教师关联关系
        self._assign_teachers_to_courses(courses)
        
        return len(courses_to_create)
    
    def _assign_teachers_to_courses(self, courses: List[Dict]) -> None:
        """为课程分配教师"""
        self.stdout.write("   🔗 分配课程教师...")
        
        teachers = list(User.objects.filter(user_type='teacher'))
        courses_objs = list(Course.objects.all())
        
        if not teachers:
            self.stdout.write("   ⚠️  没有教师数据，跳过教师分配")
            return
        
        # 为每门课程随机分配1-2个教师
        import random
        for course_obj in courses_objs:
            num_teachers = random.randint(1, min(2, len(teachers)))
            assigned_teachers = random.sample(teachers, num_teachers)
            course_obj.teachers.set(assigned_teachers)
    
    def _import_enrollments(self, enrollments: List[Dict], batch_size: int) -> int:
        """导入选课数据"""
        # 获取学生和课程映射
        students = User.objects.filter(user_type='student')
        courses = Course.objects.all()
        
        if not students.exists() or not courses.exists():
            self.stdout.write("   ⚠️  缺少学生或课程数据，跳过选课导入")
            return 0
        
        student_map = {s.student_id: s for s in students}
        course_map = {c.code: c for c in courses}
        
        enrollments_to_create = []
        
        for enrollment_data in enrollments:
            student_id = enrollment_data.get('student_id')
            course_code = enrollment_data.get('course_code')
            
            if student_id in student_map and course_code in course_map:
                enrollment = Enrollment(
                    student=student_map[student_id],
                    course=course_map[course_code],
                    status=enrollment_data.get('status', 'enrolled'),
                    score=enrollment_data.get('score'),
                    grade=enrollment_data.get('grade', ''),
                    is_active=enrollment_data.get('is_active', True)
                )
                enrollments_to_create.append(enrollment)
        
        # 去重处理（学生-课程组合唯一）
        unique_enrollments = {}
        for enrollment in enrollments_to_create:
            key = (enrollment.student_id, enrollment.course_id)
            if key not in unique_enrollments:
                unique_enrollments[key] = enrollment
        
        final_enrollments = list(unique_enrollments.values())
        Enrollment.objects.bulk_create(final_enrollments, batch_size=batch_size)
        
        return len(final_enrollments)
    
    def _show_import_results(self, import_stats: Dict[str, int]) -> None:
        """显示导入结果"""
        self.stdout.write("\n📊 导入结果统计:")
        self.stdout.write("-" * 40)
        
        total_imported = 0
        for data_type, count in import_stats.items():
            total_imported += count
            self.stdout.write(f"  ✅ {data_type}: {count:,} 条")
        
        self.stdout.write(f"  📈 总计: {total_imported:,} 条记录")
    
    def _validate_imported_data(self) -> None:
        """验证导入的数据"""
        self.stdout.write("\n🔍 验证导入数据...")
        
        # 检查数据完整性
        checks = [
            ('用户', User.objects.count()),
            ('学生档案', StudentProfile.objects.count()),
            ('教师档案', TeacherProfile.objects.count()),
            ('课程', Course.objects.count()),
            ('选课记录', Enrollment.objects.count()),
            ('教室', Classroom.objects.count()),
            ('时间段', TimeSlot.objects.count()),
        ]
        
        for name, count in checks:
            self.stdout.write(f"  📋 {name}: {count:,} 条")
        
        # 检查关联关系
        courses_with_teachers = Course.objects.filter(teachers__isnull=False).distinct().count()
        self.stdout.write(f"  🔗 有教师的课程: {courses_with_teachers} 门")
        
        enrollments_count = Enrollment.objects.filter(is_active=True).count()
        self.stdout.write(f"  📚 有效选课记录: {enrollments_count} 条")
        
        self.stdout.write("  ✅ 数据验证完成")