from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import time as dtime
import math
import json

from apps.classrooms.models import Building, Classroom
from apps.schedules.models import TimeSlot, Schedule
from apps.courses.models import Course
from apps.schedules.algorithms import create_auto_schedule


class Command(BaseCommand):
    help = "Seed parameterized full dataset (2-hour timeslots, buildings/classrooms/teachers/courses) and auto-schedule for a semester."

    def add_arguments(self, parser):
        parser.add_argument('--semester', default='2025-2026-1')
        parser.add_argument('--academic_year', default='2025-2026')
        parser.add_argument('--num_buildings', type=int, default=4)
        parser.add_argument('--num_classrooms', type=int, default=80)
        parser.add_argument('--num_teachers', type=int, default=60)
        parser.add_argument('--num_courses', type=int, default=200)

    def _ensure_timeslots(self):
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

    def _ensure_buildings(self, n: int):
        buildings = []
        for i in range(n):
            code = chr(ord('A') + i)
            b, _ = Building.objects.get_or_create(code=code, defaults={'name': f'{code}号教学楼', 'address': '校区'})
            buildings.append(b)
        return buildings

    def _capacity_for_room_type(self, rtype: str) -> int:
        if rtype == 'lecture':
            return 80
        if rtype == 'multimedia':
            return 100
        if rtype == 'auditorium':
            return 160
        if rtype == 'computer':
            return 80
        if rtype == 'lab':
            return 50
        return 60

    def _ensure_classrooms(self, buildings, total_rooms: int):
        types_cycle = ['lecture', 'multimedia', 'auditorium', 'computer', 'lab']
        per = max(1, total_rooms // max(1, len(buildings)))
        rem = total_rooms - per * len(buildings)
        created = 0
        for idx, b in enumerate(buildings):
            cnt = per + (1 if idx < rem else 0)
            # generate room numbers deterministically to avoid collisions
            floor = 1
            number = 1
            for i in range(cnt):
                room_number = f"{floor}{number:02d}"
                number += 1
                if number > 20:
                    number = 1
                    floor += 1
                rtype = types_cycle[(i + idx) % len(types_cycle)]
                cap = self._capacity_for_room_type(rtype)
                Classroom.objects.get_or_create(
                    building=b,
                    room_number=room_number,
                    defaults={
                        'name': f'{b.code}{room_number}',
                        'capacity': cap,
                        'room_type': rtype,
                        'floor': int(room_number[0]),
                        'equipment': {
                            'projector': rtype in ['lecture', 'multimedia', 'auditorium', 'seminar'],
                            'ac': True,
                            'computer': rtype in ['computer', 'lab'],
                        },
                        'is_available': True,
                        'is_active': True,
                    }
                )
                created += 1
        return created

    def _ensure_teachers(self, n: int):
        User = get_user_model()
        teachers = []
        for i in range(1, n + 1):
            username = f't_{i:03d}'
            # generate a unique employee_id that won't collide with existing ones
            # start from a higher range to avoid earlier seeds like T0001..
            eid_num = 10000 + i
            emp_id = f'T{eid_num}'
            while User.objects.filter(employee_id=emp_id).exists():
                eid_num += 1
                emp_id = f'T{eid_num}'

            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'user_type': 'teacher',
                    'employee_id': emp_id,
                    'first_name': '教',
                    'last_name': f'师{i:03d}',
                    'email': f'{username}@example.com',
                    'department': '计算机学院',
                }
            )
            changed = False
            if u.user_type != 'teacher':
                u.user_type = 'teacher'; changed = True
            if not u.employee_id:
                # assign a unique employee_id for existing user without one
                eid_num2 = eid_num
                emp_id2 = emp_id
                while User.objects.filter(employee_id=emp_id2).exclude(pk=u.pk).exists():
                    eid_num2 += 1
                    emp_id2 = f'T{eid_num2}'
                u.employee_id = emp_id2; changed = True
            if created:
                u.set_password('pass1234')
                changed = True
            if changed:
                u.save()
            teachers.append(u)
        return teachers

    def _ensure_courses(self, semester: str, academic_year: str, teachers, n: int):
        created_courses = []
        for i in range(1, n + 1):
            code = f'CSE{i + 10000}'  # avoid collision with earlier minimal seeds
            defaults = {
                'name': f'课程{i:03d}',
                'english_name': '',
                'credits': 2 + (i % 3),
                'hours': 36,
                'course_type': 'required' if i % 2 else 'elective',
                'department': '计算机学院',
                'semester': semester,
                'academic_year': academic_year,
                'description': '自动生成课程',
                'max_students': 80 if i % 3 else 100,
                'min_students': 10,
                'is_active': True,
                'is_published': True,
            }
            course, created = Course.objects.get_or_create(code=code, defaults=defaults)
            if created:
                # Assign 1-2 teachers round-robin
                if teachers:
                    idx = (i - 1) % len(teachers)
                    teacher_list = [teachers[idx]]
                    if (i % 5 == 0) and len(teachers) > 1:
                        teacher_list.append(teachers[(idx + 7) % len(teachers)])
                    course.teachers.set(teacher_list)
                    course.save()
                created_courses.append(course)
            else:
                changed = False
                if course.semester != semester:
                    course.semester = semester; changed = True
                if course.academic_year != academic_year:
                    course.academic_year = academic_year; changed = True
                if changed:
                    course.save()
        return created_courses

    @transaction.atomic
    def handle(self, *args, **options):
        semester = options['semester']
        academic_year = options['academic_year']
        num_buildings = int(options['num_buildings'])
        num_classrooms = int(options['num_classrooms'])
        num_teachers = int(options['num_teachers'])
        num_courses = int(options['num_courses'])

        self._ensure_timeslots()
        buildings = self._ensure_buildings(num_buildings)
        self._ensure_classrooms(buildings, num_classrooms)
        teachers = self._ensure_teachers(num_teachers)
        self._ensure_courses(semester, academic_year, teachers, num_courses)

        # Auto schedule
        result = create_auto_schedule(semester, academic_year, None, 'greedy', 120)
        created_schedules = []
        algo = result.get('algorithm_instance')
        if algo:
            with transaction.atomic():
                for s in algo.create_schedules():
                    s.save()
                    created_schedules.append(s)

        counts = {
            'buildings': Building.objects.count(),
            'classrooms': Classroom.objects.count(),
            'teachers': get_user_model().objects.filter(user_type='teacher').count(),
            'timeslots_active': TimeSlot.objects.filter(is_active=True).count(),
            'courses_in_semester': Course.objects.filter(semester=semester).count(),
            'schedules_in_semester': Schedule.objects.filter(semester=semester, status='active').count(),
            'created_schedules_count': len(created_schedules),
        }
        self.stdout.write(json.dumps({'semester': semester, 'academic_year': academic_year, 'counts': counts}, ensure_ascii=False))
