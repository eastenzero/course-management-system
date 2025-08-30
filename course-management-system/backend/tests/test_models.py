"""
Tests for model methods and business logic.
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

from tests.factories import (
    UserFactory, StudentUserFactory, TeacherUserFactory, AdminUserFactory,
    CourseFactory, ClassroomFactory, BuildingFactory,
    TimeSlotFactory, ScheduleFactory, EnrollmentFactory
)
from apps.courses.models import Course, Enrollment, Grade
from apps.classrooms.models import Classroom, Building
from apps.schedules.models import TimeSlot, Schedule
from apps.users.models import User

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test User model methods and validation."""
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = StudentUserFactory(username='testuser', user_type='student')
        expected = 'testuser - 学生'
        self.assertEqual(str(user), expected)
    
    def test_display_id_for_student(self):
        """Test display_id property for student."""
        student = StudentUserFactory(student_id='S123456')
        self.assertEqual(student.display_id, 'S123456')
    
    def test_display_id_for_teacher(self):
        """Test display_id property for teacher."""
        teacher = TeacherUserFactory(employee_id='T123456')
        self.assertEqual(teacher.display_id, 'T123456')
    
    def test_student_validation_requires_student_id(self):
        """Test that students must have student_id."""
        with self.assertRaises(ValidationError) as cm:
            user = User(
                username='student',
                email='student@test.com',
                user_type='student'
                # Missing student_id
            )
            user.clean()
        
        self.assertIn('student_id', cm.exception.message_dict)
    
    def test_teacher_validation_requires_employee_id(self):
        """Test that teachers must have employee_id."""
        with self.assertRaises(ValidationError) as cm:
            user = User(
                username='teacher',
                email='teacher@test.com',
                user_type='teacher'
                # Missing employee_id
            )
            user.clean()
        
        self.assertIn('employee_id', cm.exception.message_dict)
    
    def test_superuser_skips_validation(self):
        """Test that superusers skip validation."""
        user = User(
            username='admin',
            email='admin@test.com',
            user_type='student',  # Would normally require student_id
            is_superuser=True
        )
        # Should not raise ValidationError
        user.clean()


@pytest.mark.django_db
class TestCourseModel:
    """Test Course model methods and validation."""
    
    def test_course_str_representation(self):
        """Test course string representation."""
        course = CourseFactory(code='CS101', name='Introduction to Programming')
        expected = 'CS101 - Introduction to Programming'
        assert str(course) == expected
    
    def test_course_current_enrollment_property(self):
        """Test current_enrollment property."""
        course = CourseFactory()

        # Create some enrollments
        EnrollmentFactory.create_batch(3, course=course, status='enrolled', is_active=True)
        EnrollmentFactory(course=course, status='dropped', is_active=False)  # Should not count

        assert course.current_enrollment == 3
    
    def test_course_is_full_property(self):
        """Test is_full property."""
        course = CourseFactory(max_students=2)
        
        # Course is not full initially
        assert not course.is_full
        
        # Add students up to limit
        EnrollmentFactory.create_batch(2, course=course, status='enrolled')
        
        # Refresh from database
        course.refresh_from_db()
        assert course.is_full
    
    def test_course_can_open_property(self):
        """Test can_open property."""
        course = CourseFactory(min_students=2)
        
        # Course cannot open initially
        assert not course.can_open
        
        # Add minimum students
        EnrollmentFactory.create_batch(2, course=course, status='enrolled')
        
        # Refresh from database
        course.refresh_from_db()
        assert course.can_open
    
    def test_course_validation_min_max_students(self):
        """Test course validation for min/max students."""
        with pytest.raises(ValidationError):
            course = Course(
                name='Test Course',
                code='TEST101',
                credits=3,
                hours=48,
                department='Test Dept',
                semester='2024-2025-1',
                min_students=10,
                max_students=5  # Invalid: min > max
            )
            course.clean()


class EnrollmentModelTestCase(TestCase):
    """Test Enrollment model methods and validation."""
    
    def test_enrollment_str_representation(self):
        """Test enrollment string representation."""
        student = StudentUserFactory(username='student1')
        course = CourseFactory(name='Test Course')
        enrollment = EnrollmentFactory(student=student, course=course)
        
        expected = 'student1 - Test Course'
        self.assertEqual(str(enrollment), expected)
    
    def test_enrollment_unique_constraint(self):
        """Test that student cannot enroll in same course twice."""
        student = StudentUserFactory()
        course = CourseFactory()
        
        # First enrollment should succeed
        enrollment1 = EnrollmentFactory(student=student, course=course)
        
        # Second enrollment should fail due to unique constraint
        with self.assertRaises(Exception):  # IntegrityError in real database
            EnrollmentFactory(student=student, course=course)


@pytest.mark.django_db
class TestClassroomModel:
    """Test Classroom model methods and validation."""
    
    def test_classroom_str_representation(self):
        """Test classroom string representation."""
        building = BuildingFactory(name='Science Building', code='SCI')
        classroom = ClassroomFactory(name='Room 101', room_number='101', building=building)

        expected = 'SCI-101'
        assert str(classroom) == expected
    
    def test_building_str_representation(self):
        """Test building string representation."""
        building = BuildingFactory(name='Main Building', code='MB')
        expected = 'MB - Main Building'
        assert str(building) == expected


@pytest.mark.django_db
class TestScheduleModel:
    """Test Schedule model methods and validation."""
    
    def test_time_slot_str_representation(self):
        """Test time slot string representation."""
        from datetime import time
        time_slot = TimeSlotFactory(
            name='第1节',
            start_time=time(8, 0),
            end_time=time(9, 40)
        )
        expected = '第1节 (08:00:00-09:40:00)'
        assert str(time_slot) == expected
    
    def test_time_slot_duration_calculation(self):
        """Test time slot duration calculation."""
        from datetime import time
        time_slot = TimeSlot(
            name='第1节',
            start_time=time(8, 0),
            end_time=time(9, 40),
            order=1
        )
        time_slot.save()
        
        # Duration should be 100 minutes
        assert time_slot.duration_minutes == 100
    
    def test_schedule_str_representation(self):
        """Test schedule string representation."""
        teacher = TeacherUserFactory(username='teacher1')
        course = CourseFactory(name='Test Course', teachers=[teacher])
        schedule = ScheduleFactory(
            course=course,
            teacher=teacher,
            day_of_week=1  # Monday
        )

        # Check that the string contains the expected components
        schedule_str = str(schedule)
        assert 'Test Course' in schedule_str
        assert '周一' in schedule_str
        assert '第' in schedule_str and '节' in schedule_str


@pytest.mark.django_db
class TestBusinessLogic:
    """Test business logic and complex operations."""
    
    def test_student_enrollment_workflow(self):
        """Test complete student enrollment workflow."""
        student = StudentUserFactory()
        course = CourseFactory(max_students=2, min_students=1)
        
        # Student enrolls in course
        enrollment = EnrollmentFactory(student=student, course=course)
        
        # Verify enrollment
        assert enrollment.status == 'enrolled'
        assert enrollment.student == student
        assert enrollment.course == course
        assert enrollment.is_active
        
        # Verify course enrollment count
        course.refresh_from_db()
        assert course.current_enrollment == 1
        assert course.can_open
        assert not course.is_full
    
    def test_course_capacity_management(self):
        """Test course capacity management."""
        course = CourseFactory(max_students=2)
        
        # Enroll students up to capacity
        student1 = StudentUserFactory()
        student2 = StudentUserFactory()
        
        EnrollmentFactory(student=student1, course=course)
        EnrollmentFactory(student=student2, course=course)
        
        # Course should be full
        course.refresh_from_db()
        assert course.is_full
        assert course.current_enrollment == 2
    
    def test_teacher_course_assignment(self):
        """Test teacher assignment to courses."""
        teacher1 = TeacherUserFactory()
        teacher2 = TeacherUserFactory()
        course = CourseFactory(teachers=[teacher1, teacher2])
        
        # Verify teachers are assigned
        assert teacher1 in course.teachers.all()
        assert teacher2 in course.teachers.all()
        assert course.teachers.count() == 2
    
    def test_schedule_conflict_detection_data_setup(self):
        """Test data setup for schedule conflict detection."""
        teacher = TeacherUserFactory()
        classroom = ClassroomFactory()
        time_slot = TimeSlotFactory()
        course1 = CourseFactory(teachers=[teacher])
        course2 = CourseFactory(teachers=[teacher])
        
        # Create first schedule
        schedule1 = ScheduleFactory(
            course=course1,
            teacher=teacher,
            classroom=classroom,
            time_slot=time_slot,
            day_of_week=1,
            semester='2024-2025-1'
        )
        
        # Verify schedule creation
        assert schedule1.course == course1
        assert schedule1.teacher == teacher
        assert schedule1.classroom == classroom
        assert schedule1.time_slot == time_slot
        
        # Note: Actual conflict detection would be implemented in business logic
        # This test just verifies the data setup for conflict scenarios
