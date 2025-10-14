"""
教师模块测试
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.courses.models import Course
from apps.teachers.models import TeacherProfile, TeacherCourseAssignment, TeacherNotice
from apps.teachers.services import TeacherService

User = get_user_model()


class TeacherProfileTestCase(TestCase):
    """教师档案测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001',
            first_name='李',
            last_name='老师'
        )
    
    def test_teacher_profile_creation(self):
        """测试教师档案创建"""
        profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            title='副教授',
            research_area='人工智能',
            office_location='A楼301',
            teaching_experience=5,
            education_background='博士',
            bio='专注于机器学习和深度学习研究'
        )
        
        self.assertEqual(profile.user, self.teacher_user)
        self.assertEqual(profile.title, '副教授')
        self.assertEqual(profile.research_area, '人工智能')
        self.assertEqual(profile.office_location, 'A楼301')
        self.assertEqual(profile.teaching_experience, 5)
        self.assertEqual(profile.education_background, '博士')
    
    def test_teacher_profile_str(self):
        """测试教师档案字符串表示"""
        profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            title='副教授',
            research_area='人工智能'
        )
        
        expected_str = f"{self.teacher_user.username} - 副教授"
        self.assertEqual(str(profile), expected_str)
    
    def test_teacher_profile_defaults(self):
        """测试教师档案默认值"""
        profile = TeacherProfile.objects.create(
            user=self.teacher_user
        )
        
        self.assertEqual(profile.title, '讲师')
        self.assertEqual(profile.research_area, '未指定')
        self.assertEqual(profile.office_location, '未指定')
        self.assertEqual(profile.teaching_experience, 0)
        self.assertTrue(profile.is_active_teacher)


class TeacherCourseAssignmentTestCase(TestCase):
    """教师课程分配测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
        )
        
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            title='副教授'
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
    
    def test_course_assignment_creation(self):
        """测试课程分配创建"""
        assignment = TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course,
            role='primary',
            workload_hours=48,
            semester='2024-2025-1'
        )
        
        self.assertEqual(assignment.teacher, self.teacher_profile)
        self.assertEqual(assignment.course, self.course)
        self.assertEqual(assignment.role, 'primary')
        self.assertEqual(assignment.workload_hours, 48)
        self.assertEqual(assignment.semester, '2024-2025-1')
    
    def test_course_assignment_str(self):
        """测试课程分配字符串表示"""
        assignment = TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course,
            role='primary',
            semester='2024-2025-1'
        )
        
        expected_str = f"{self.teacher_user.username} - {self.course.name} (2024-2025-1)"
        self.assertEqual(str(assignment), expected_str)


class TeacherNoticeTestCase(TestCase):
    """教师通知测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
        )
        
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user
        )
    
    def test_teacher_notice_creation(self):
        """测试教师通知创建"""
        notice = TeacherNotice.objects.create(
            teacher=self.teacher_profile,
            title='期末考试安排',
            content='请各位老师注意期末考试时间安排...',
            notice_type='exam',
            priority='high'
        )
        
        self.assertEqual(notice.teacher, self.teacher_profile)
        self.assertEqual(notice.title, '期末考试安排')
        self.assertEqual(notice.notice_type, 'exam')
        self.assertEqual(notice.priority, 'high')
        self.assertTrue(notice.is_active)
    
    def test_teacher_notice_str(self):
        """测试教师通知字符串表示"""
        notice = TeacherNotice.objects.create(
            teacher=self.teacher_profile,
            title='期末考试安排',
            notice_type='exam'
        )
        
        expected_str = f"{self.teacher_user.username} - 期末考试安排"
        self.assertEqual(str(notice), expected_str)


class TeacherServiceTestCase(TestCase):
    """教师服务测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
        )
        
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            title='副教授'
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
            code='CS102',
            name='程序设计基础',
            course_type='required',
            credits=4,
            hours=64,
            department='计算机学院',
            semester='2024-2025-1',
            academic_year='2024-2025',
            max_students=80,
            min_students=15
        )
    
    def test_get_teacher_dashboard_data(self):
        """测试获取教师仪表板数据"""
        # 创建课程分配
        TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course1,
            role='primary',
            workload_hours=48,
            semester='2024-2025-1'
        )
        
        TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course2,
            role='assistant',
            workload_hours=32,
            semester='2024-2025-1'
        )
        
        dashboard_data = TeacherService.get_teacher_dashboard_data(self.teacher_user)
        
        self.assertIn('assigned_courses', dashboard_data)
        self.assertIn('total_workload', dashboard_data)
        self.assertIn('total_students', dashboard_data)
        self.assertEqual(dashboard_data['assigned_courses'], 2)
        self.assertEqual(dashboard_data['total_workload'], 80)  # 48 + 32
    
    def test_get_teacher_courses(self):
        """测试获取教师课程"""
        # 创建课程分配
        TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course1,
            role='primary',
            semester='2024-2025-1'
        )
        
        courses = TeacherService.get_teacher_courses(
            self.teacher_user,
            semester='2024-2025-1'
        )
        
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]['code'], 'CS101')
        self.assertEqual(courses[0]['name'], '计算机科学导论')
    
    def test_get_teacher_workload(self):
        """测试获取教师工作量"""
        # 创建课程分配
        TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course1,
            role='primary',
            workload_hours=48,
            semester='2024-2025-1'
        )
        
        TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course2,
            role='assistant',
            workload_hours=32,
            semester='2024-2025-1'
        )
        
        workload = TeacherService.get_teacher_workload(
            self.teacher_user,
            semester='2024-2025-1'
        )
        
        self.assertEqual(workload['total_hours'], 80)
        self.assertEqual(workload['course_count'], 2)
        self.assertEqual(len(workload['courses']), 2)


class TeacherAPITestCase(APITestCase):
    """教师API测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
        )
        
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            title='副教授'
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
    
    def test_get_teacher_profile_unauthorized(self):
        """测试未授权用户无法获取教师档案"""
        url = reverse('teachers:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_teacher_profile_authorized(self):
        """测试授权用户可以获取教师档案"""
        self.client.force_authenticate(user=self.teacher_user)
        
        url = reverse('teachers:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        profile_data = response.data['data']
        self.assertEqual(profile_data['title'], '副教授')
    
    def test_update_teacher_profile(self):
        """测试更新教师档案"""
        self.client.force_authenticate(user=self.teacher_user)
        
        url = reverse('teachers:profile')
        data = {
            'title': '教授',
            'research_area': '机器学习',
            'office_location': 'B楼201',
            'bio': '专注于深度学习研究'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证数据已更新
        self.teacher_profile.refresh_from_db()
        self.assertEqual(self.teacher_profile.title, '教授')
        self.assertEqual(self.teacher_profile.research_area, '机器学习')
    
    def test_get_teacher_dashboard(self):
        """测试获取教师仪表板"""
        self.client.force_authenticate(user=self.teacher_user)
        
        url = reverse('teachers:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        dashboard_data = response.data['data']
        self.assertIn('assigned_courses', dashboard_data)
        self.assertIn('total_workload', dashboard_data)
    
    def test_get_teacher_courses(self):
        """测试获取教师课程"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # 创建课程分配
        TeacherCourseAssignment.objects.create(
            teacher=self.teacher_profile,
            course=self.course,
            role='primary',
            semester='2024-2025-1'
        )
        
        url = reverse('teachers:courses')
        response = self.client.get(url, {'semester': '2024-2025-1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        courses_data = response.data['data']
        self.assertEqual(len(courses_data), 1)
        self.assertEqual(courses_data[0]['code'], 'CS101')
