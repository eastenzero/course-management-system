from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import time as dtime
import json

from apps.classrooms.models import Building, Classroom
from apps.schedules.models import TimeSlot, Schedule
from apps.courses.models import Course
from apps.schedules.algorithms import create_auto_schedule


class Command(BaseCommand):
    help = "Seed minimal data (buildings, classrooms, teachers, courses, timeslots) and run auto-schedule for a semester."

    def add_arguments(self, parser):
        parser.add_argument('--semester', default='2025-2026-1')
        parser.add_argument('--academic_year', default='2025-2026')
        parser.add_argument('--teachers', type=int, default=6)
        parser.add_argument('--courses', type=int, default=10)

    @transaction.atomic
    def handle(self, *args, **options):
        semester = options['semester']
        academic_year = options['academic_year']
        teacher_count = int(options['teachers'])
        course_count = int(options['courses'])
        User = get_user_model()

        # Buildings
        bA, _ = Building.objects.get_or_create(code='A', defaults={'name': 'A号教学楼', 'address': '校区'})
        bB, _ = Building.objects.get_or_create(code='B', defaults={'name': 'B号教学楼', 'address': '校区'})

        # TimeSlots (2-hour blocks)
        ts_defs = [
            (1, '08:00-10:00', dtime(8, 0), dtime(10, 0)),
            (2, '10:10-12:10', dtime(10, 10), dtime(12, 10)),
            (3, '14:00-16:00', dtime(14, 0), dtime(16, 0)),
            (4, '16:10-18:10', dtime(16, 10), dtime(18, 10)),
            (5, '19:00-21:00', dtime(19, 0), dtime(21, 0)),
        ]
        for order, name, start, end in ts_defs:
            TimeSlot.objects.get_or_create(
                order=order,
                defaults={
                    'name': name,
                    'start_time': start,
                    'end_time': end,
                    'is_active': True,
                }
            )

        # Classrooms
        rooms = [
            (bA, '101', 40, 'lecture', 1),
            (bA, '201', 80, 'multimedia', 2),
            (bA, '301', 120, 'auditorium', 3),
            (bB, '101', 60, 'lecture', 1),
        ]
        for b, rn, cap, rtype, floor in rooms:
            Classroom.objects.get_or_create(
                building=b,
                room_number=rn,
                defaults={
                    'name': f'{b.code}{rn}',
                    'capacity': cap,
                    'room_type': rtype,
                    'floor': floor,
                    'equipment': {
                        'projector': rtype in ['lecture', 'multimedia', 'auditorium', 'seminar'],
                        'ac': True,
                        'computer': rtype in ['computer', 'lab'],
                    },
                    'is_available': True,
                    'is_active': True,
                }
            )

        # Teachers
        teachers = []
        for i in range(1, teacher_count + 1):
            username = f'teacher{i:03d}'
            employee_id = f'T{i:04d}'
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'user_type': 'teacher',
                    'employee_id': employee_id,
                    'first_name': '教',
                    'last_name': f'师{i:03d}',
                    'email': f'{username}@example.com',
                    'department': '计算机学院',
                }
            )
            # Ensure fields for existing user
            changed = False
            if u.user_type != 'teacher':
                u.user_type = 'teacher'; changed = True
            if not u.employee_id:
                u.employee_id = employee_id; changed = True
            if created:
                u.set_password('pass1234')
                changed = True
            if changed:
                u.save()
            teachers.append(u)

        # Courses
        created_courses = []
        for i in range(1, course_count + 1):
            code = f'CS{100 + i}'
            defaults = {
                'name': f'课程{i:03d}',
                'english_name': '',
                'credits': 2 + (i % 3),
                'hours': 36,  # 2h x 18 weeks => ~1 session/week
                'course_type': 'required' if i % 2 else 'elective',
                'department': '计算机学院',
                'semester': semester,
                'academic_year': academic_year,
                'description': '自动生成的示例课程',
                'max_students': 60 if i % 2 else 80,
                'min_students': 10,
                'is_active': True,
                'is_published': True,
            }
            course, created = Course.objects.get_or_create(code=code, defaults=defaults)
            if created:
                # Bind teacher (round-robin)
                t = teachers[(i - 1) % len(teachers)]
                course.teachers.set([t])
                course.save()
                created_courses.append(course)
            else:
                # Ensure semester alignment if exists
                changed = False
                if course.semester != semester:
                    course.semester = semester; changed = True
                if course.academic_year != academic_year:
                    course.academic_year = academic_year; changed = True
                if changed:
                    course.save()

        # Run auto-schedule
        result = create_auto_schedule(semester, academic_year, None, 'greedy', 120)
        algo = result.get('algorithm_instance')
        created_schedules = []
        if algo:
            with transaction.atomic():
                for s in algo.create_schedules():
                    s.save()
                    created_schedules.append(s)

        # Counts
        counts = {
            'buildings': Building.objects.count(),
            'classrooms': Classroom.objects.count(),
            'teachers': User.objects.filter(user_type='teacher').count(),
            'timeslots_active': TimeSlot.objects.filter(is_active=True).count(),
            'courses_in_semester': Course.objects.filter(semester=semester).count(),
            'schedules_in_semester': Schedule.objects.filter(semester=semester, status='active').count(),
            'created_schedules_count': len(created_schedules),
        }
        self.stdout.write(json.dumps({'semester': semester, 'academic_year': academic_year, 'counts': counts}, ensure_ascii=False))
