"""
Django管理命令：导入测试数据
用于将data-generator生成的JSON数据导入到Django数据库中
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime, parse_date, parse_time

from apps.users.models import User
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Building, Classroom
from apps.schedules.models import TimeSlot, Schedule


class Command(BaseCommand):
    help = '导入测试数据到Django数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='JSON数据文件路径（相对于项目根目录）',
            default='../data-generator/output/json/course_data_20250814_135816.json'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空现有数据',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行，不实际导入数据',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始导入测试数据...'))
        
        # 获取文件路径
        file_path = options['file']
        if not os.path.isabs(file_path):
            # 相对路径，基于项目根目录
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            file_path = os.path.join(base_dir, file_path)
        
        if not os.path.exists(file_path):
            raise CommandError(f'数据文件不存在: {file_path}')
        
        # 读取JSON数据
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.stdout.write(f'成功读取数据文件: {file_path}')
        except Exception as e:
            raise CommandError(f'读取数据文件失败: {e}')
        
        # 验证数据结构
        required_keys = ['departments', 'students', 'teachers', 'courses', 'classrooms', 'time_slots']
        for key in required_keys:
            if key not in data:
                raise CommandError(f'数据文件缺少必需的键: {key}')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('试运行模式，不会实际导入数据'))
            self._print_data_summary(data)
            return
        
        # 清空现有数据
        if options['clear']:
            self._clear_existing_data()
        
        # 开始导入数据
        try:
            with transaction.atomic():
                self._import_data(data)
            self.stdout.write(self.style.SUCCESS('数据导入完成！'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'数据导入失败: {e}'))
            raise

    def _print_data_summary(self, data):
        """打印数据摘要"""
        self.stdout.write('\n=== 数据摘要 ===')
        for key, items in data.items():
            if isinstance(items, list):
                self.stdout.write(f'{key}: {len(items)} 条记录')
        self.stdout.write('================\n')

    def _clear_existing_data(self):
        """清空现有数据"""
        self.stdout.write('清空现有数据...')
        
        # 按依赖关系顺序删除
        Schedule.objects.all().delete()
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Classroom.objects.all().delete()
        Building.objects.all().delete()
        TimeSlot.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # 保留超级用户
        
        self.stdout.write('现有数据已清空')

    def _import_data(self, data):
        """导入数据"""
        self.stdout.write('开始导入数据...')
        
        # 1. 导入时间段
        self._import_time_slots(data.get('time_slots', []))
        
        # 2. 导入教学楼和教室
        self._import_classrooms(data.get('classrooms', []))
        
        # 3. 导入用户（学生和教师）
        self._import_students(data.get('students', []))
        self._import_teachers(data.get('teachers', []))
        
        # 4. 导入课程
        self._import_courses(data.get('courses', []))
        
        # 5. 导入选课记录
        self._import_enrollments(data.get('enrollments', []))
        
        # 6. 导入排课记录（如果有）
        if 'schedules' in data:
            self._import_schedules(data.get('schedules', []))

    def _import_time_slots(self, time_slots):
        """导入时间段"""
        self.stdout.write('导入时间段...')

        for slot_data in time_slots:
            # 解析时间字符串
            start_time = parse_time(slot_data['start_time'])
            end_time = parse_time(slot_data['end_time'])

            TimeSlot.objects.get_or_create(
                id=slot_data['id'],
                defaults={
                    'name': slot_data['name'],
                    'start_time': start_time,
                    'end_time': end_time,
                    'order': slot_data.get('order', slot_data['id']),
                    'is_active': slot_data.get('is_active', True),
                }
            )

        self.stdout.write(f'导入时间段: {len(time_slots)} 条')

    def _import_classrooms(self, classrooms):
        """导入教室"""
        self.stdout.write('导入教室...')
        
        # 先创建教学楼
        buildings = {}
        for classroom_data in classrooms:
            building_name = classroom_data.get('building', '主教学楼')
            if building_name not in buildings:
                building, created = Building.objects.get_or_create(
                    name=building_name,
                    defaults={
                        'code': f'BUILD{len(buildings)+1:03d}',
                        'address': f'{building_name}地址',
                        'description': f'{building_name}描述',
                        'is_active': True,
                    }
                )
                buildings[building_name] = building
        
        # 创建教室
        for classroom_data in classrooms:
            building_name = classroom_data.get('building', '主教学楼')
            building = buildings[building_name]
            
            # 映射教室类型
            room_type_mapping = {
                '普通教室': 'lecture',
                '实验室': 'lab', 
                '机房': 'computer',
                '多媒体教室': 'multimedia',
                '研讨室': 'seminar',
                '阶梯教室': 'auditorium',
            }
            
            room_type = room_type_mapping.get(
                classroom_data.get('type', '普通教室'), 
                'lecture'
            )
            
            Classroom.objects.get_or_create(
                building=building,
                room_number=classroom_data['room_number'],
                defaults={
                    'name': classroom_data.get('name', ''),
                    'capacity': classroom_data['capacity'],
                    'room_type': room_type,
                    'floor': classroom_data.get('floor', 1),
                    'area': classroom_data.get('area'),
                    'equipment': classroom_data.get('equipment', {}),
                    'location_description': classroom_data.get('location_description', ''),
                    'is_available': classroom_data.get('is_available', True),
                    'is_active': classroom_data.get('is_active', True),
                }
            )
        
        self.stdout.write(f'导入教室: {len(classrooms)} 条')

    def _import_students(self, students):
        """导入学生"""
        self.stdout.write('导入学生...')

        # 批量导入，提高性能
        batch_size = 100
        for i in range(0, len(students), batch_size):
            batch = students[i:i + batch_size]

            for student_data in batch:
                try:
                    # 解析姓名
                    name = student_data.get('name', '')
                    name_parts = name.split() if name else ['', '']
                    first_name = name_parts[-1] if len(name_parts) > 1 else name
                    last_name = name_parts[0] if len(name_parts) > 1 else ''

                    User.objects.get_or_create(
                        username=student_data['username'],
                        defaults={
                            'password': make_password('123456'),  # 默认密码
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': student_data.get('email', f"{student_data['username']}@student.edu.cn"),
                            'user_type': 'student',
                            'student_id': student_data['student_id'],
                            'department': student_data.get('department', '未分配'),
                            'phone': student_data.get('phone', ''),
                            'is_active': True,
                        }
                    )
                except Exception as e:
                    self.stdout.write(f'导入学生失败: {student_data.get("username", "unknown")} - {e}')
                    continue

            # 显示进度
            if (i + batch_size) % 1000 == 0 or (i + batch_size) >= len(students):
                self.stdout.write(f'已导入学生: {min(i + batch_size, len(students))}/{len(students)}')

        self.stdout.write(f'导入学生完成: {len(students)} 条')

    def _import_teachers(self, teachers):
        """导入教师"""
        self.stdout.write('导入教师...')

        for teacher_data in teachers:
            try:
                # 解析姓名
                name = teacher_data.get('name', '')
                name_parts = name.split() if name else ['', '']
                first_name = name_parts[-1] if len(name_parts) > 1 else name
                last_name = name_parts[0] if len(name_parts) > 1 else ''

                User.objects.get_or_create(
                    username=teacher_data['username'],
                    defaults={
                        'password': make_password('123456'),  # 默认密码
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': teacher_data.get('email', f"{teacher_data['username']}@teacher.edu.cn"),
                        'user_type': 'teacher',
                        'employee_id': teacher_data['employee_id'],
                        'department': teacher_data.get('department', '未分配'),
                        'phone': teacher_data.get('phone', ''),
                        'is_active': True,
                    }
                )
            except Exception as e:
                self.stdout.write(f'导入教师失败: {teacher_data.get("username", "unknown")} - {e}')
                continue

        self.stdout.write(f'导入教师: {len(teachers)} 条')

    def _import_courses(self, courses):
        """导入课程"""
        self.stdout.write('导入课程...')

        for course_data in courses:
            # 映射课程类型
            course_type_mapping = {
                '必修': 'required',
                '选修': 'elective',
                '限选': 'elective',
                '通识': 'public',
                '专业': 'professional',
            }

            course_type = course_type_mapping.get(
                course_data.get('type', '选修'),
                'elective'
            )

            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'name': course_data['name'],
                    'english_name': course_data.get('english_name', ''),
                    'credits': course_data.get('credits', 2),
                    'hours': course_data.get('hours', 32),
                    'course_type': course_type,
                    'department': course_data.get('department', ''),
                    'semester': course_data.get('semester', '2024-2025-1'),
                    'academic_year': course_data.get('academic_year', '2024-2025'),
                    'description': course_data.get('description', ''),
                    'objectives': course_data.get('objectives', ''),
                    'max_students': course_data.get('max_students', 50),
                    'min_students': course_data.get('min_students', 10),
                    'is_active': course_data.get('is_active', True),
                    'is_published': course_data.get('is_published', True),
                }
            )

            # 添加授课教师
            if 'teacher_ids' in course_data:
                for teacher_id in course_data['teacher_ids']:
                    try:
                        teacher = User.objects.get(employee_id=f'T{teacher_id:06d}')
                        course.teachers.add(teacher)
                    except User.DoesNotExist:
                        continue

        self.stdout.write(f'导入课程: {len(courses)} 条')

    def _import_enrollments(self, enrollments):
        """导入选课记录"""
        self.stdout.write('导入选课记录...')

        # 预加载用户和课程数据以提高性能
        students_map = {user.id: user for user in User.objects.filter(user_type='student')}
        courses_map = {course.id: course for course in Course.objects.all()}

        batch_size = 1000
        success_count = 0

        for i in range(0, len(enrollments), batch_size):
            batch = enrollments[i:i + batch_size]

            for enrollment_data in batch:
                try:
                    student_id = enrollment_data.get('student_id')
                    course_id = enrollment_data.get('course_id')

                    # 根据数据格式查找学生和课程
                    student = None
                    course = None

                    if isinstance(student_id, int):
                        # 如果是数字ID，需要找到对应的学生
                        student = students_map.get(student_id)
                    else:
                        # 如果是字符串ID，按student_id查找
                        try:
                            student = User.objects.get(student_id=student_id, user_type='student')
                        except User.DoesNotExist:
                            continue

                    if isinstance(course_id, int):
                        # 如果是数字ID，需要找到对应的课程
                        course = courses_map.get(course_id)
                    else:
                        # 如果是字符串ID，按code查找
                        try:
                            course = Course.objects.get(code=course_id)
                        except Course.DoesNotExist:
                            continue

                    if student and course:
                        # 映射状态
                        status_mapping = {
                            '已选': 'enrolled',
                            '已退': 'dropped',
                            '已完成': 'completed',
                            '未通过': 'failed',
                        }
                        status = status_mapping.get(enrollment_data.get('status', '已选'), 'enrolled')

                        Enrollment.objects.get_or_create(
                            student=student,
                            course=course,
                            defaults={
                                'status': status,
                                'score': enrollment_data.get('score'),
                            }
                        )
                        success_count += 1

                except Exception as e:
                    continue

            # 显示进度
            if (i + batch_size) % 5000 == 0 or (i + batch_size) >= len(enrollments):
                self.stdout.write(f'已处理选课记录: {min(i + batch_size, len(enrollments))}/{len(enrollments)}，成功: {success_count}')

        self.stdout.write(f'导入选课记录完成: {success_count}/{len(enrollments)} 条')

    def _import_schedules(self, schedules):
        """导入排课记录"""
        self.stdout.write('导入排课记录...')

        for schedule_data in schedules:
            try:
                course = Course.objects.get(code=schedule_data['course_code'])
                classroom = Classroom.objects.get(
                    building__name=schedule_data['building'],
                    room_number=schedule_data['room_number']
                )
                teacher = User.objects.get(employee_id=schedule_data['teacher_id'])
                time_slot = TimeSlot.objects.get(id=schedule_data['time_slot_id'])

                Schedule.objects.get_or_create(
                    course=course,
                    classroom=classroom,
                    teacher=teacher,
                    time_slot=time_slot,
                    day_of_week=schedule_data['day_of_week'],
                    defaults={
                        'week_start': schedule_data.get('week_start', 1),
                        'week_end': schedule_data.get('week_end', 18),
                        'status': 'active',
                    }
                )
            except (Course.DoesNotExist, Classroom.DoesNotExist, User.DoesNotExist, TimeSlot.DoesNotExist):
                continue

        self.stdout.write(f'导入排课记录: {len(schedules)} 条')
