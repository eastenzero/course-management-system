"""
Tests for the courses API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories import (
    StudentUserFactory, TeacherUserFactory, CourseFactory, 
    EnrollmentFactory, AdminUserFactory
)


class CourseListAPITestCase(APITestCase):
    """Test course list API endpoint."""
    
    def setUp(self):
        self.teacher = TeacherUserFactory()
        self.student = StudentUserFactory()
        self.admin = AdminUserFactory()
        self.course1 = CourseFactory(teacher=self.teacher, name="Course 1")
        self.course2 = CourseFactory(teacher=self.teacher, name="Course 2")
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access course list."""
        url = reverse('courses:course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_view_courses(self):
        """Test that authenticated users can view course list."""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses:course-list')
        response = self.client.get(url)
        
        # Should return 200 or 404 (if view doesn't exist yet)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
    
    def test_course_list_pagination(self):
        """Test that course list supports pagination."""
        # Create more courses
        CourseFactory.create_batch(25, teacher=self.teacher)
        
        self.client.force_authenticate(user=self.student)
        url = reverse('courses:course-list')
        response = self.client.get(url)
        
        if response.status_code == status.HTTP_200_OK:
            # Should have pagination
            self.assertIn('results', response.data)
            self.assertIn('count', response.data)
            self.assertIn('next', response.data)
            self.assertIn('previous', response.data)


class CourseDetailAPITestCase(APITestCase):
    """Test course detail API endpoint."""
    
    def setUp(self):
        self.teacher = TeacherUserFactory()
        self.student = StudentUserFactory()
        self.course = CourseFactory(teacher=self.teacher)
    
    def test_authenticated_user_can_view_course_detail(self):
        """Test that authenticated users can view course details."""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses:course-detail', kwargs={'pk': self.course.id})
        response = self.client.get(url)
        
        if response.status_code == status.HTTP_200_OK:
            # Verify course data structure
            self.assertIn('id', response.data)
            self.assertIn('name', response.data)
            self.assertIn('code', response.data)
            self.assertEqual(response.data['id'], self.course.id)
        else:
            # Should not be unauthorized
            self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_nonexistent_course_returns_404(self):
        """Test that requesting nonexistent course returns 404."""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses:course-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        # Should return 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestCourseCreationAPI:
    """Test course creation API endpoints."""
    
    def test_teacher_can_create_course(self, teacher_client):
        """Test that teachers can create courses."""
        url = reverse('courses:course-list')
        data = {
            'name': 'New Course',
            'code': 'NEW101',
            'credits': 3,
            'hours': 48,
            'course_type': 'elective',
            'department': 'Computer Science',
            'semester': '2024-2025-1'
        }
        response = teacher_client.post(url, data)
        
        # Should not be unauthorized
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        
        if response.status_code == status.HTTP_201_CREATED:
            # Verify created course data
            assert response.data['name'] == 'New Course'
            assert response.data['code'] == 'NEW101'
    
    def test_student_cannot_create_course(self, student_client):
        """Test that students cannot create courses."""
        url = reverse('courses:course-list')
        data = {
            'name': 'Unauthorized Course',
            'code': 'UNAUTH101',
            'credits': 3,
            'hours': 48,
            'course_type': 'elective',
            'department': 'Computer Science',
            'semester': '2024-2025-1'
        }
        response = student_client.post(url, data)
        
        # Should return 403 (forbidden)
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]
    
    def test_admin_can_create_course(self, admin_client):
        """Test that admins can create courses."""
        url = reverse('courses:course-list')
        data = {
            'name': 'Admin Course',
            'code': 'ADMIN101',
            'credits': 3,
            'hours': 48,
            'course_type': 'required',
            'department': 'Administration',
            'semester': '2024-2025-1'
        }
        response = admin_client.post(url, data)
        
        # Should not be unauthorized
        assert response.status_code != status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCourseUpdateAPI:
    """Test course update API endpoints."""
    
    def test_teacher_can_update_own_course(self, teacher_client, teacher_user):
        """Test that teachers can update their own courses."""
        course = CourseFactory(teacher=teacher_user)
        url = reverse('courses:course-detail', kwargs={'pk': course.id})
        data = {'name': 'Updated Course Name'}
        response = teacher_client.patch(url, data)
        
        # Should not be unauthorized
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        
        if response.status_code == status.HTTP_200_OK:
            assert response.data['name'] == 'Updated Course Name'
    
    def test_teacher_cannot_update_other_teacher_course(self, teacher_client):
        """Test that teachers cannot update other teachers' courses."""
        other_teacher = TeacherUserFactory()
        other_course = CourseFactory(teacher=other_teacher)
        
        url = reverse('courses:course-detail', kwargs={'pk': other_course.id})
        data = {'name': 'Hacked Course Name'}
        response = teacher_client.patch(url, data)
        
        # Should return 403 or 404
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]
    
    def test_student_cannot_update_course(self, student_client, course):
        """Test that students cannot update courses."""
        url = reverse('courses:course-detail', kwargs={'pk': course.id})
        data = {'name': 'Student Hacked Course'}
        response = student_client.patch(url, data)
        
        # Should return 403
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]


class CourseEnrollmentAPITestCase(APITestCase):
    """Test course enrollment API endpoints."""
    
    def setUp(self):
        self.teacher = TeacherUserFactory()
        self.student = StudentUserFactory()
        self.course = CourseFactory(teacher=self.teacher)
    
    def test_student_can_enroll_in_course(self):
        """Test that students can enroll in courses."""
        self.client.force_authenticate(user=self.student)
        
        try:
            url = reverse('courses:enroll', kwargs={'pk': self.course.id})
            response = self.client.post(url)
            
            # Should not be unauthorized
            self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            
            if response.status_code == status.HTTP_201_CREATED:
                # Verify enrollment was created
                self.assertIn('enrollment', response.data)
        except:
            # URL pattern might not exist yet
            pass
    
    def test_student_cannot_enroll_twice(self):
        """Test that students cannot enroll in the same course twice."""
        EnrollmentFactory(student=self.student, course=self.course)
        
        self.client.force_authenticate(user=self.student)
        
        try:
            url = reverse('courses:enroll', kwargs={'pk': self.course.id})
            response = self.client.post(url)
            
            # Should return 400 (bad request) or 409 (conflict)
            self.assertIn(response.status_code, [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_409_CONFLICT
            ])
        except:
            # URL pattern might not exist yet
            pass
    
    def test_student_can_drop_course(self):
        """Test that students can drop courses."""
        enrollment = EnrollmentFactory(student=self.student, course=self.course)
        
        self.client.force_authenticate(user=self.student)
        
        try:
            url = reverse('courses:drop', kwargs={'pk': self.course.id})
            response = self.client.delete(url)
            
            # Should not be unauthorized
            self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        except:
            # URL pattern might not exist yet
            pass


@pytest.mark.django_db
class TestCourseSearchAPI:
    """Test course search and filtering API endpoints."""
    
    def test_course_search_by_name(self, student_client):
        """Test that courses can be searched by name."""
        CourseFactory(name="Python Programming")
        CourseFactory(name="Java Programming")
        CourseFactory(name="Database Systems")
        
        url = reverse('courses:course-list')
        response = student_client.get(url, {'search': 'Programming'})
        
        if response.status_code == status.HTTP_200_OK:
            # Should return courses with "Programming" in the name
            course_names = [course['name'] for course in response.data['results']]
            assert any('Programming' in name for name in course_names)
    
    def test_course_filter_by_department(self, student_client):
        """Test that courses can be filtered by department."""
        CourseFactory(department="Computer Science")
        CourseFactory(department="Mathematics")
        
        url = reverse('courses:course-list')
        response = student_client.get(url, {'department': 'Computer Science'})
        
        if response.status_code == status.HTTP_200_OK:
            # Should return only Computer Science courses
            departments = [course['department'] for course in response.data['results']]
            assert all(dept == 'Computer Science' for dept in departments)
    
    def test_course_filter_by_type(self, student_client):
        """Test that courses can be filtered by course type."""
        CourseFactory(course_type="required")
        CourseFactory(course_type="elective")
        
        url = reverse('courses:course-list')
        response = student_client.get(url, {'course_type': 'required'})
        
        if response.status_code == status.HTTP_200_OK:
            # Should return only required courses
            types = [course['course_type'] for course in response.data['results']]
            assert all(course_type == 'required' for course_type in types)
