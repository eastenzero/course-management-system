"""
Factory classes for creating test data using factory_boy.
"""

import factory
from datetime import time
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import TimeSlot, Schedule

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    user_type = 'student'
    student_id = factory.Sequence(lambda n: f"U{n:06d}")


class StudentUserFactory(UserFactory):
    """Factory for creating Student users."""
    user_type = 'student'
    student_id = factory.Sequence(lambda n: f"S{n:06d}")


class TeacherUserFactory(UserFactory):
    """Factory for creating Teacher users."""
    user_type = 'teacher'
    employee_id = factory.Sequence(lambda n: f"T{n:06d}")


class AdminUserFactory(UserFactory):
    """Factory for creating Admin users."""
    user_type = 'admin'
    employee_id = factory.Sequence(lambda n: f"A{n:06d}")
    is_staff = True
    is_superuser = True


class CourseFactory(factory.django.DjangoModelFactory):
    """Factory for creating Course instances."""

    class Meta:
        model = Course
        skip_postgeneration_save = True

    name = factory.Faker('sentence', nb_words=3)
    code = factory.Sequence(lambda n: f"CS{n:03d}")
    credits = factory.Faker('random_int', min=1, max=6)
    hours = factory.Faker('random_int', min=16, max=64)
    course_type = factory.Faker('random_element', elements=['required', 'elective', 'public'])
    semester = '2024-2025-1'
    department = factory.Faker('company')

    @factory.post_generation
    def teachers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # If teachers are provided, add them
            for teacher in extracted:
                self.teachers.add(teacher)
        else:
            # Create a default teacher
            teacher = TeacherUserFactory()
            self.teachers.add(teacher)


class BuildingFactory(factory.django.DjangoModelFactory):
    """Factory for creating Building instances."""
    
    class Meta:
        model = Building
    
    name = factory.Faker('company')
    code = factory.Sequence(lambda n: f"B{n:02d}")
    address = factory.Faker('address')


class ClassroomFactory(factory.django.DjangoModelFactory):
    """Factory for creating Classroom instances."""

    class Meta:
        model = Classroom

    name = factory.Sequence(lambda n: f"Room {n:03d}")
    room_number = factory.Sequence(lambda n: f"{n:03d}")
    capacity = factory.Faker('random_int', min=20, max=200)
    room_type = factory.Faker('random_element', elements=['lecture', 'lab', 'seminar'])
    floor = factory.Faker('random_int', min=1, max=10)
    building = factory.SubFactory(BuildingFactory)


class TimeSlotFactory(factory.django.DjangoModelFactory):
    """Factory for creating TimeSlot instances."""

    class Meta:
        model = TimeSlot

    name = factory.Sequence(lambda n: f"第{n+1}节")
    order = factory.Sequence(lambda n: n+1)
    start_time = time(8, 0)  # 8:00 AM
    end_time = time(9, 40)   # 9:40 AM
    duration_minutes = 100


class ScheduleFactory(factory.django.DjangoModelFactory):
    """Factory for creating Schedule instances."""

    class Meta:
        model = Schedule

    course = factory.SubFactory(CourseFactory)
    time_slot = factory.SubFactory(TimeSlotFactory)
    classroom = factory.SubFactory(ClassroomFactory)
    teacher = factory.SubFactory(TeacherUserFactory)
    day_of_week = factory.Faker('random_int', min=1, max=7)
    week_range = "1-18周"
    semester = '2024-2025-1'
    academic_year = '2024-2025'


class EnrollmentFactory(factory.django.DjangoModelFactory):
    """Factory for creating Enrollment instances."""

    class Meta:
        model = Enrollment

    student = factory.SubFactory(StudentUserFactory)
    course = factory.SubFactory(CourseFactory)
    status = 'enrolled'
    is_active = True
    is_active = True
