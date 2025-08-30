"""
算法模块测试
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.courses.models import Course
from apps.classrooms.models import Building, Classroom
from apps.schedules.models import TimeSlot, Schedule
from apps.schedules.algorithms import SchedulingAlgorithm, ScheduleConstraint

User = get_user_model()


class SchedulingAlgorithmTestCase(TestCase):
    """排课算法测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建用户
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
        )
        
        # 创建课程
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
        self.course.teachers.add(self.teacher)
        
        # 创建教学楼和教室
        self.building = Building.objects.create(
            code='A',
            name='A栋教学楼',
            address='校园内'
        )
        
        self.classroom = Classroom.objects.create(
            building=self.building,
            room_number='101',
            capacity=120,
            room_type='lecture',
            floor=1
        )
        
        # 创建时间段
        self.time_slot = TimeSlot.objects.create(
            name='第1节',
            order=1,
            start_time='08:00',
            end_time='08:45'
        )
        
        # 创建排课算法实例
        self.algorithm = SchedulingAlgorithm('2024-2025-1', '2024-2025')
    
    def test_algorithm_initialization(self):
        """测试算法初始化"""
        self.assertEqual(self.algorithm.semester, '2024-2025-1')
        self.assertEqual(self.algorithm.academic_year, '2024-2025')
        self.assertEqual(len(self.algorithm.constraints), 0)
        self.assertEqual(len(self.algorithm.assigned_slots), 0)
    
    def test_add_constraint(self):
        """测试添加约束"""
        constraint = ScheduleConstraint(
            course=self.course,
            teacher=self.teacher,
            sessions_per_week=2
        )
        
        self.algorithm.add_constraint(constraint)
        self.assertEqual(len(self.algorithm.constraints), 1)
        self.assertEqual(self.algorithm.constraints[0], constraint)
    
    def test_conflict_detection(self):
        """测试冲突检测"""
        from apps.schedules.algorithms import ScheduleSlot
        
        # 创建时间槽
        slot = ScheduleSlot(
            day_of_week=1,  # 周一
            time_slot=self.time_slot,
            classroom=self.classroom
        )
        
        # 测试无冲突情况
        self.assertFalse(self.algorithm.check_teacher_conflict(self.teacher, slot))
        self.assertFalse(self.algorithm.check_classroom_conflict(self.classroom, slot))
    
    def test_schedule_generation(self):
        """测试课程表生成"""
        constraint = ScheduleConstraint(
            course=self.course,
            teacher=self.teacher,
            sessions_per_week=2
        )
        
        self.algorithm.add_constraint(constraint)
        
        # 添加可用时间槽
        from apps.schedules.algorithms import ScheduleSlot
        slot = ScheduleSlot(
            day_of_week=1,
            time_slot=self.time_slot,
            classroom=self.classroom
        )
        self.algorithm.available_slots.add(slot)
        
        # 运行算法
        result = self.algorithm.solve()
        
        # 验证结果
        self.assertIn('successful_assignments', result)
        self.assertIn('failed_assignments', result)
        self.assertIn('total_constraints', result)
        self.assertIn('success_rate', result)


class AlgorithmAPITestCase(APITestCase):
    """算法API测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            user_type='admin',
            is_staff=True
        )
        
        # 创建教师用户
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
        )
        
        # 创建课程
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
        self.course.teachers.add(self.teacher)
    
    def test_generate_schedule_unauthorized(self):
        """测试未授权用户无法生成课程表"""
        url = reverse('algorithms:generate-schedule')
        data = {
            'semester': '2024-2025-1',
            'academic_year': '2024-2025'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_generate_schedule_authorized(self):
        """测试授权用户可以生成课程表"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('algorithms:generate-schedule')
        data = {
            'semester': '2024-2025-1',
            'academic_year': '2024-2025'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        result_data = response.data['data']
        self.assertIn('successful_assignments', result_data)
        self.assertIn('failed_assignments', result_data)
    
    def test_check_conflicts(self):
        """测试冲突检查API"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('algorithms:check-conflicts')
        data = {
            'semester': '2024-2025-1'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        result_data = response.data['data']
        self.assertIn('conflicts', result_data)
        self.assertIn('total_conflicts', result_data)
    
    def test_optimize_schedule(self):
        """测试课程表优化API"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('algorithms:optimize-schedule')
        data = {
            'semester': '2024-2025-1',
            'optimization_type': 'minimize_conflicts'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证响应数据
        self.assertIn('data', response.data)
        result_data = response.data['data']
        self.assertIn('optimization_result', result_data)


class ConstraintTestCase(TestCase):
    """约束条件测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            user_type='teacher',
            employee_id='T001'
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
    
    def test_schedule_constraint_creation(self):
        """测试排课约束创建"""
        constraint = ScheduleConstraint(
            course=self.course,
            teacher=self.teacher,
            sessions_per_week=2
        )
        
        self.assertEqual(constraint.course, self.course)
        self.assertEqual(constraint.teacher, self.teacher)
        self.assertEqual(constraint.sessions_per_week, 2)
        self.assertEqual(len(constraint.preferred_days), 0)
        self.assertEqual(len(constraint.preferred_time_slots), 0)
        self.assertEqual(len(constraint.preferred_classrooms), 0)
    
    def test_constraint_priority(self):
        """测试约束优先级"""
        constraint1 = ScheduleConstraint(
            course=self.course,
            teacher=self.teacher,
            sessions_per_week=2,
            priority=1
        )
        
        constraint2 = ScheduleConstraint(
            course=self.course,
            teacher=self.teacher,
            sessions_per_week=3,
            priority=2
        )
        
        self.assertLess(constraint1.priority, constraint2.priority)
