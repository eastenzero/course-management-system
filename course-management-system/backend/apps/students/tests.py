"""
学生模块测试
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment
from apps.students.models import StudentProfile, StudentCourseProgress
from apps.students.services import StudentService

User = get_user_model()


class StudentProfileTestCase(TestCase):
    """学生档案测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            user_type='student',
            student_id='S001',
            first_name='张',
            last_name='三'
        )
    
    def test_student_profile_creation(self):
        """测试学生档案创建"""
        profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_year=2024,
            major='计算机科学与技术',
            class_name='计科1班',
            gpa=3.5,
            total_credits=60
        )
        
        self.assertEqual(profile.user, self.student_user)
        self.assertEqual(profile.admission_year, 2024)
        self.assertEqual(profile.major, '计算机科学与技术')
        self.assertEqual(profile.class_name, '计科1班')
        self.assertEqual(profile.gpa, 3.5)
        self.assertEqual(profile.total_credits, 60)
    
    def test_student_profile_str(self):
        """测试学生档案字符串表示"""
        profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_year=2024,
            major='计算机科学与技术'
        )
        
        expected_str = f"{self.student_user.username} - 计算机科学与技术"
        self.assertEqual(str(profile), expected_str)
    
    def test_student_profile_gpa_validation(self):
        """测试GPA验证"""
        # 测试有效GPA
        profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_year=2024,
            major='计算机科学与技术',
            gpa=3.8
        )
        self.assertEqual(profile.gpa, 3.8)
        
        # 测试GPA边界值
        profile.gpa = 0.0
        profile.save()
        self.assertEqual(profile.gpa, 0.0)
        
        profile.gpa = 4.0
        profile.save()
        self.assertEqual(profile.gpa, 4.0)


class StudentCourseProgressTestCase(TestCase):
    """学生课程进度测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            user_type='student',
            student_id='S001'
        )
        
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_year=2024,
            major='计算机科学与技术'
        )
        
        self.course = Course.objects.create(
            code='CS101',
            name='计算机科学导论',
            course_type='required',
            credits=3,
            hours=48,
            department='计算机学院',
            semester='2024-2025-1',
            academic_year='2024-2025',
            max_students=100,
            min_students=20
        )
        
        self.enrollment = Enrollment.objects.create(
            student=self.student_user,
            course=self.course,
            status='enrolled'
        )
    
    def test_course_progress_creation(self):
        """测试课程进度创建"""
        progress = StudentCourseProgress.objects.create(
            student=self.student_profile,
            course=self.course,
            completion_percentage=75.5,
            last_activity_date='2024-01-15'
        )
        
        self.assertEqual(progress.student, self.student_profile)
        self.assertEqual(progress.course, self.course)
        self.assertEqual(progress.completion_percentage, 75.5)
    
    def test_course_progress_str(self):
        """测试课程进度字符串表示"""
        progress = StudentCourseProgress.objects.create(
            student=self.student_profile,
            course=self.course,
            completion_percentage=80.0
        )
        
        expected_str = f"{self.student_user.username} - {self.course.name} (80.0%)"
        self.assertEqual(str(progress), expected_str)


class StudentServiceTestCase(TestCase):
    """学生服务测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            user_type='student',
            student_id='S001'
        )
        
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_year=2024,
            major='计算机科学与技术'
        )
        
        self.course1 = Course.objects.create(
            code='CS101',
            name='计算机科学导论',
            course_type='required',
            credits=3,
            hours=48,
            department='计算机学院',
            semester='2024-2025-1',
            academic_year='2024-2025',
            max_students=100,
            min_students=20
        )
        
        self.course2 = Course.objects.create(
            code='MATH101',
            name='高等数学',
            course_type='required',
            credits=4,
            hours=64,
            department='数学学院',
            semester='2024-2025-1',
            academic_year='2024-2025',
            max_students=150,
            min_students=30
        )
    
    def test_get_student_dashboard_data(self):
        """测试获取学生仪表板数据"""
        # 创建选课记录
        Enrollment.objects.create(
            student=self.student_user,
            course=self.course1,
            status='enrolled'
        )
        
        Enrollment.objects.create(
            student=self.student_user,
            course=self.course2,
            status='enrolled'
        )
        
        dashboard_data = StudentService.get_student_dashboard_data(self.student_user)
        
        self.assertIn('enrolled_courses', dashboard_data)
        self.assertIn('total_credits', dashboard_data)
        self.assertIn('gpa', dashboard_data)
        self.assertEqual(dashboard_data['enrolled_courses'], 2)
        self.assertEqual(dashboard_data['total_credits'], 7)  # 3 + 4
    
    def test_get_available_courses(self):
        """测试获取可选课程"""
        available_courses = StudentService.get_available_courses(
            semester='2024-2025-1'
        )
        
        self.assertGreaterEqual(len(available_courses), 2)
        
        # 验证课程信息
        course_codes = [course['code'] for course in available_courses]
        self.assertIn('CS101', course_codes)
        self.assertIn('MATH101', course_codes)
    
    def test_enroll_course(self):
        """测试选课"""
        result = StudentService.enroll_course(self.student_user, self.course1.id)
        
        self.assertTrue(result['success'])
        self.assertIn('enrollment', result)
        
        # 验证选课记录已创建
        enrollment = Enrollment.objects.get(
            student=self.student_user,
            course=self.course1
        )
        self.assertEqual(enrollment.status, 'enrolled')
    
    def test_drop_course(self):
        """测试退课"""
        # 先选课
        enrollment = Enrollment.objects.create(
            student=self.student_user,
            course=self.course1,
            status='enrolled'
        )
        
        result = StudentService.drop_course(self.student_user, self.course1.id)
        
        self.assertTrue(result['success'])
        
        # 验证选课记录状态已更新
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'dropped')


class StudentAPITestCase(APITestCase):
    """学生API测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            user_type='student',
            student_id='S001'
        )
        
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            admission_year=2024,
            major='计算机科学与技术'
        )
        
        self.course = Course.objects.create(
            code='CS101',
            name='计算机科学导论',
            course_type='required',
            credits=3,
            hours=48,
            department='计算机学院',
            semester='2024-2025-1',
            academic_year='2024-2025',
            max_students=100,
            min_students=20
        )
    
    def test_get_student_profile_unauthorized(self):
        """测试未授权用户无法获取学生档案"""
        url = reverse('students:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_student_profile_authorized(self):
        """测试授权用户可以获取学生档案"""
        self.client.force_authenticate(user=self.student_user)
        
        url = reverse('students:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        profile_data = response.data['data']
        self.assertEqual(profile_data['major'], '计算机科学与技术')
        self.assertEqual(profile_data['admission_year'], 2024)
    
    def test_update_student_profile(self):
        """测试更新学生档案"""
        self.client.force_authenticate(user=self.student_user)
        
        url = reverse('students:profile')
        data = {
            'major': '软件工程',
            'class_name': '软工1班',
            'emergency_contact': '李四',
            'emergency_phone': '13800138000'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证数据已更新
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.major, '软件工程')
        self.assertEqual(self.student_profile.class_name, '软工1班')
    
    def test_get_dashboard_data(self):
        """测试获取仪表板数据"""
        self.client.force_authenticate(user=self.student_user)
        
        url = reverse('students:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        dashboard_data = response.data['data']
        self.assertIn('enrolled_courses', dashboard_data)
        self.assertIn('total_credits', dashboard_data)
        self.assertIn('gpa', dashboard_data)
    
    def test_enroll_course_api(self):
        """测试选课API"""
        self.client.force_authenticate(user=self.student_user)
        
        url = reverse('students:enroll')
        data = {'course_id': self.course.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证选课记录已创建
        enrollment_exists = Enrollment.objects.filter(
            student=self.student_user,
            course=self.course,
            status='enrolled'
        ).exists()
        self.assertTrue(enrollment_exists)
