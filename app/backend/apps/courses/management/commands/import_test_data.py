import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import Schedule, TimeSlot

User = get_user_model()


class Command(BaseCommand):
    help = '导入测试数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='JSON数据文件路径（相对于项目根目录）',
            default='data-generator/output/json/course_data_20250814_135816.json'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空现有数据',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_data = options['clear']
        
        # 构建完整文件路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        full_path = os.path.join(base_dir, '..', '..', file_path)
        
        if not os.path.exists(full_path):
            raise CommandError(f'数据文件不存在: {full_path}')
        
        self.stdout.write(f'开始导入数据文件: {full_path}')
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f'读取数据文件失败: {e}')
        
        if clear_data:
            self.clear_existing_data()
        
        with transaction.atomic():
            self.import_data(data)
        
        self.stdout.write(
            self.style.SUCCESS('数据导入完成！')
        )

    def clear_existing_data(self):
        """清空现有数据"""
        self.stdout.write('清空现有数据...')
        
        # 按依赖关系顺序删除
        Enrollment.objects.all().delete()
        Schedule.objects.all().delete()
        Course.objects.all().delete()
        TimeSlot.objects.all().delete()
        Classroom.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write('现有数据已清空')

    def import_data(self, data):
        """导入数据"""
        self.stdout.write('开始导入数据...')

        # 创建ID映射表
        self.student_id_map = {}  # 原始ID -> 数据库ID
        self.course_id_map = {}   # 原始ID -> 数据库ID

        # 1. 导入时间段
        self.import_time_slots(data.get('time_slots', []))

        # 2. 导入教学楼和教室
        self.import_buildings_and_classrooms(data.get('classrooms', []))

        # 3. 导入用户（学生和教师）
        self.import_students(data.get('students', []))
        self.import_teachers(data.get('teachers', []))

        # 4. 导入课程
        self.import_courses(data.get('courses', []))

        # 5. 导入选课记录
        self.import_enrollments(data.get('enrollments', []))

        self.stdout.write('所有数据导入完成')

    def import_time_slots(self, time_slots):
        """导入时间段"""
        self.stdout.write('导入时间段...')

        for slot_data in time_slots:
            TimeSlot.objects.get_or_create(
                id=slot_data['id'],
                defaults={
                    'name': slot_data['name'],
                    'start_time': slot_data['start_time'],
                    'end_time': slot_data['end_time'],
                    'order': slot_data['id'],  # 使用ID作为排序
                    'is_active': slot_data.get('is_active', True)
                }
            )

        self.stdout.write(f'导入了 {len(time_slots)} 个时间段')

    def import_buildings_and_classrooms(self, classrooms):
        """导入教学楼和教室"""
        self.stdout.write('导入教学楼和教室...')

        # 先创建教学楼
        buildings = {}
        for room_data in classrooms:
            building_name = room_data['building']
            if building_name not in buildings:
                building, created = Building.objects.get_or_create(
                    name=building_name,
                    defaults={
                        'code': building_name[:10],  # 简化代码
                        'is_active': True
                    }
                )
                buildings[building_name] = building

        # 再创建教室
        for room_data in classrooms:
            building = buildings[room_data['building']]
            Classroom.objects.get_or_create(
                building=building,
                room_number=room_data['room_number'],
                defaults={
                    'name': room_data.get('name', ''),
                    'floor': room_data['floor'],
                    'capacity': room_data['capacity'],
                    'room_type': self.map_room_type(room_data['type']),
                    'equipment': room_data.get('equipment', {}),
                    'is_active': room_data.get('is_active', True),
                    'location_description': room_data.get('description', '')
                }
            )

        self.stdout.write(f'导入了 {len(buildings)} 个教学楼和 {len(classrooms)} 个教室')

    def import_students(self, students):
        """导入学生"""
        self.stdout.write('导入学生...')

        for i, student_data in enumerate(students):
            user, created = User.objects.get_or_create(
                username=student_data['student_id'],
                defaults={
                    'first_name': student_data['name'],
                    'email': student_data['email'],
                    'user_type': 'student',
                    'student_id': student_data['student_id'],
                    'department': student_data['major'],
                    'phone': student_data.get('phone', ''),
                    'is_active': student_data.get('is_active', True)
                }
            )
            if created:
                user.set_password('123456')  # 默认密码
                user.save()

            # 每处理1000条记录显示进度
            if (i + 1) % 1000 == 0:
                self.stdout.write(f'已导入学生: {i + 1}/{len(students)}')

        # 建立学生ID映射
        self.stdout.write('建立学生ID映射...')
        for student_data in students:
            try:
                user = User.objects.get(student_id=student_data['student_id'])
                self.student_id_map[student_data['id']] = user.id
            except User.DoesNotExist:
                pass

        self.stdout.write(f'导入学生完成: {len(students)} 条，映射: {len(self.student_id_map)} 条')

    def import_teachers(self, teachers):
        """导入教师"""
        self.stdout.write('导入教师...')
        
        for teacher_data in teachers:
            user, created = User.objects.get_or_create(
                username=teacher_data['employee_id'],
                defaults={
                    'first_name': teacher_data['name'],
                    'email': teacher_data['email'],
                    'user_type': 'teacher',
                    'employee_id': teacher_data['employee_id'],
                    'department': teacher_data['department'],
                    'phone': teacher_data.get('phone', ''),
                    'is_active': teacher_data.get('is_active', True)
                }
            )
            if created:
                user.set_password('123456')  # 默认密码
                user.save()
        
        self.stdout.write(f'导入了 {len(teachers)} 个教师')

    def import_courses(self, courses):
        """导入课程"""
        self.stdout.write('导入课程...')
        
        for course_data in courses:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'english_name': course_data.get('english_name', ''),
                    'credits': course_data['credits'],
                    'hours': course_data['hours'],
                    'course_type': self.map_course_type(course_data['type']),
                    'department': course_data['department'],
                    'semester': course_data.get('semester', '2024-2025-1'),
                    'academic_year': course_data.get('academic_year', '2024-2025'),
                    'description': course_data.get('description', ''),
                    'max_students': course_data.get('max_students', 50),
                    'min_students': course_data.get('min_students', 10),
                    'is_active': course_data.get('is_active', True),
                    'is_published': course_data.get('is_published', True)
                }
            )

            # 添加授课教师
            if 'teacher_id' in course_data:
                try:
                    teacher = User.objects.get(employee_id=course_data['teacher_id'])
                    course.teachers.add(teacher)
                except User.DoesNotExist:
                    pass

        # 建立课程ID映射
        self.stdout.write('建立课程ID映射...')
        for course_data in courses:
            try:
                course = Course.objects.get(code=course_data['code'])
                self.course_id_map[course_data['id']] = course.id
            except Course.DoesNotExist:
                pass

        self.stdout.write(f'导入课程完成: {len(courses)} 门，映射: {len(self.course_id_map)} 条')

    def import_enrollments(self, enrollments):
        """导入选课记录"""
        self.stdout.write('导入选课记录...')

        success_count = 0
        total_count = len(enrollments)

        for i, enrollment_data in enumerate(enrollments):
            try:
                # 使用ID映射查找学生和课程
                student_db_id = self.student_id_map.get(enrollment_data['student_id'])
                course_db_id = self.course_id_map.get(enrollment_data['course_id'])

                if not student_db_id or not course_db_id:
                    continue

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

                # 每处理5000条记录显示进度
                if (i + 1) % 5000 == 0:
                    self.stdout.write(f'已处理选课记录: {i + 1}/{total_count}，成功: {success_count}')

            except (User.DoesNotExist, Course.DoesNotExist) as e:
                continue

        self.stdout.write(f'导入选课记录完成: {success_count}/{total_count} 条')

    def map_course_type(self, original_type):
        """映射课程类型"""
        type_mapping = {
            '必修': 'required',
            '选修': 'elective',
            '限选': 'elective',
            '通识': 'public'
        }
        return type_mapping.get(original_type, 'elective')

    def map_room_type(self, original_type):
        """映射教室类型"""
        type_mapping = {
            '普通教室': 'lecture',
            '实验室': 'lab',
            '机房': 'computer',
            '多媒体教室': 'multimedia',
            '研讨室': 'seminar',
            '阶梯教室': 'auditorium',
            '工作室': 'studio',
            '图书馆': 'library',
            '体育馆': 'gym'
        }
        return type_mapping.get(original_type, 'lecture')
