"""
Pytest configuration and fixtures for the course management system tests.
"""

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import (
    UserFactory, StudentUserFactory, TeacherUserFactory, AdminUserFactory,
    CourseFactory, ClassroomFactory, BuildingFactory,
    TimeSlotFactory, ScheduleFactory, EnrollmentFactory
)

User = get_user_model()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def api_client():
    """DRF API test client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a basic user."""
    return UserFactory()


@pytest.fixture
def student_user():
    """Create a student user."""
    return StudentUserFactory()


@pytest.fixture
def teacher_user():
    """Create a teacher user."""
    return TeacherUserFactory()


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return AdminUserFactory()


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated with a basic user."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def student_client(api_client, student_user):
    """API client authenticated with a student user."""
    refresh = RefreshToken.for_user(student_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def teacher_client(api_client, teacher_user):
    """API client authenticated with a teacher user."""
    refresh = RefreshToken.for_user(teacher_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated with an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def course(teacher_user):
    """Create a course."""
    return CourseFactory(teachers=[teacher_user])


@pytest.fixture
def building():
    """Create a building."""
    return BuildingFactory()


@pytest.fixture
def classroom(building):
    """Create a classroom."""
    return ClassroomFactory(building=building)


@pytest.fixture
def time_slot():
    """Create a time slot."""
    return TimeSlotFactory()


@pytest.fixture
def schedule(course, time_slot, classroom, teacher_user):
    """Create a schedule."""
    return ScheduleFactory(
        course=course,
        time_slot=time_slot,
        classroom=classroom,
        teacher=teacher_user
    )


@pytest.fixture
def enrollment(student_user, course):
    """Create an enrollment."""
    return EnrollmentFactory(student=student_user, course=course)


@pytest.fixture
def sample_data(teacher_user, student_user, building):
    """Create a set of sample data for testing."""
    # Create courses
    courses = CourseFactory.create_batch(3, teachers=[teacher_user])
    
    # Create classrooms
    classrooms = ClassroomFactory.create_batch(2, building=building)
    
    # Create time slots
    time_slots = TimeSlotFactory.create_batch(5)
    
    # Create enrollments
    enrollments = []
    for course in courses:
        enrollments.append(EnrollmentFactory(student=student_user, course=course))
    
    return {
        'courses': courses,
        'classrooms': classrooms,
        'time_slots': time_slots,
        'enrollments': enrollments,
        'teacher': teacher_user,
        'student': student_user,
        'building': building
    }
