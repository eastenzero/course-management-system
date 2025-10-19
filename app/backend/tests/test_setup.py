"""
Basic tests to verify the test setup is working correctly.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from tests.factories import UserFactory, StudentUserFactory, TeacherUserFactory

User = get_user_model()


class TestSetupTestCase(TestCase):
    """Test that the basic test setup is working."""
    
    def test_database_connection(self):
        """Test that we can connect to the test database."""
        user_count = User.objects.count()
        self.assertEqual(user_count, 0)
    
    def test_user_factory(self):
        """Test that the user factory works."""
        user = UserFactory()
        self.assertIsInstance(user, User)
        self.assertTrue(user.username)
        self.assertTrue(user.email)
    
    def test_student_factory(self):
        """Test that the student factory works."""
        student = StudentUserFactory()
        self.assertEqual(student.user_type, 'student')
    
    def test_teacher_factory(self):
        """Test that the teacher factory works."""
        teacher = TeacherUserFactory()
        self.assertEqual(teacher.user_type, 'teacher')


@pytest.mark.django_db
class TestPytestSetup:
    """Test that pytest setup is working correctly."""
    
    def test_user_creation(self, user):
        """Test user creation with pytest fixture."""
        assert user.username
        assert user.email
        assert user.is_active
    
    def test_student_creation(self, student_user):
        """Test student user creation."""
        assert student_user.user_type == 'student'
    
    def test_teacher_creation(self, teacher_user):
        """Test teacher user creation."""
        assert teacher_user.user_type == 'teacher'


class TestAPISetup(APITestCase):
    """Test that the API test setup is working."""
    
    def test_unauthenticated_request(self):
        """Test that unauthenticated requests are handled properly."""
        response = self.client.get('/api/v1/students/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_request_setup(self):
        """Test that we can set up authenticated requests."""
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        # This should not return 401 anymore
        response = self.client.get('/api/v1/students/dashboard/')
        # It might return 403 (forbidden) or 404 (not found) but not 401 (unauthorized)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class TestAPIClientFixtures:
    """Test API client fixtures."""
    
    def test_authenticated_client(self, authenticated_client):
        """Test authenticated client fixture."""
        response = authenticated_client.get('/api/v1/students/dashboard/')
        # Should not be unauthorized
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    def test_student_client(self, student_client):
        """Test student client fixture."""
        response = student_client.get('/api/v1/students/dashboard/')
        # Should not be unauthorized
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    def test_teacher_client(self, teacher_client):
        """Test teacher client fixture."""
        response = teacher_client.get('/api/v1/teachers/dashboard/')
        # Should not be unauthorized
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
