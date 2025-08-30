import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.courses.models import Course, Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = '只导入选课记录'

    def handle(self, *args, **options):
        # 读取JSON数据
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        file_path = os.path.join(base_dir, '..', '..', 'data-generator/output/json/course_data_20250814_135816.json')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        enrollments = data.get('enrollments', [])
        students = data.get('students', [])
        courses = data.get('courses', [])
        
        self.stdout.write(f'JSON中的选课记录数量: {len(enrollments)}')
        
        # 建立ID映射
        self.stdout.write('建立学生ID映射...')
        student_id_map = {}
        for student_data in students:
            try:
                user = User.objects.get(student_id=student_data['student_id'])
                student_id_map[student_data['id']] = user.id
            except User.DoesNotExist:
                pass
        
        self.stdout.write('建立课程ID映射...')
        course_id_map = {}
        for course_data in courses:
            try:
                course = Course.objects.get(code=course_data['code'])
                course_id_map[course_data['id']] = course.id
            except Course.DoesNotExist:
                pass
        
        self.stdout.write(f'学生ID映射: {len(student_id_map)} 条')
        self.stdout.write(f'课程ID映射: {len(course_id_map)} 条')
        
        # 导入选课记录
        self.stdout.write('开始导入选课记录...')
        success_count = 0
        total_count = len(enrollments)
        
        with transaction.atomic():
            for i, enrollment_data in enumerate(enrollments):
                try:
                    student_db_id = student_id_map.get(enrollment_data['student_id'])
                    course_db_id = course_id_map.get(enrollment_data['course_id'])
                    
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
                        
                except Exception as e:
                    continue
        
        self.stdout.write(f'选课记录导入完成: {success_count}/{total_count} 条')
        self.stdout.write(self.style.SUCCESS('选课记录导入成功！'))
