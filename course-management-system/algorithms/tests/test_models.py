# file: algorithms/tests/test_models.py
# 功能: 测试数据模型

import unittest
from datetime import datetime
from ..models import Assignment, Conflict, ScheduleResult, TeacherPreference, CourseRequirement


class TestAssignment(unittest.TestCase):
    """测试Assignment模型"""
    
    def setUp(self):
        """设置测试数据"""
        self.assignment = Assignment(
            course_id=1,
            teacher_id=2,
            classroom_id=3,
            day_of_week=1,
            time_slot=1,
            semester="2024春",
            academic_year="2023-2024"
        )
    
    def test_assignment_creation(self):
        """测试分配创建"""
        self.assertEqual(self.assignment.course_id, 1)
        self.assertEqual(self.assignment.teacher_id, 2)
        self.assertEqual(self.assignment.classroom_id, 3)
        self.assertEqual(self.assignment.day_of_week, 1)
        self.assertEqual(self.assignment.time_slot, 1)
    
    def test_time_key(self):
        """测试时间键"""
        expected_key = (1, 1)
        self.assertEqual(self.assignment.time_key, expected_key)
    
    def test_teacher_time_key(self):
        """测试教师时间键"""
        expected_key = (2, 1, 1)
        self.assertEqual(self.assignment.teacher_time_key, expected_key)
    
    def test_classroom_time_key(self):
        """测试教室时间键"""
        expected_key = (3, 1, 1)
        self.assertEqual(self.assignment.classroom_time_key, expected_key)
    
    def test_invalid_day_of_week(self):
        """测试无效的星期"""
        with self.assertRaises(ValueError):
            Assignment(
                course_id=1, teacher_id=2, classroom_id=3,
                day_of_week=8, time_slot=1
            )
    
    def test_invalid_time_slot(self):
        """测试无效的时间段"""
        with self.assertRaises(ValueError):
            Assignment(
                course_id=1, teacher_id=2, classroom_id=3,
                day_of_week=1, time_slot=25
            )
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = self.assignment.to_dict()
        expected = {
            'course_id': 1,
            'teacher_id': 2,
            'classroom_id': 3,
            'day_of_week': 1,
            'time_slot': 1,
            'semester': "2024春",
            'academic_year': "2023-2024",
            'week_range': "1-16",
        }
        self.assertEqual(result, expected)
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'course_id': 1,
            'teacher_id': 2,
            'classroom_id': 3,
            'day_of_week': 1,
            'time_slot': 1,
            'semester': "2024春",
            'academic_year': "2023-2024",
            'week_range': "1-16",
        }
        assignment = Assignment.from_dict(data)
        self.assertEqual(assignment.course_id, 1)
        self.assertEqual(assignment.teacher_id, 2)
    
    def test_copy(self):
        """测试复制"""
        copy_assignment = self.assignment.copy()
        self.assertEqual(copy_assignment.course_id, self.assignment.course_id)
        self.assertIsNot(copy_assignment, self.assignment)


class TestConflict(unittest.TestCase):
    """测试Conflict模型"""
    
    def setUp(self):
        """设置测试数据"""
        self.assignment1 = Assignment(1, 2, 3, 1, 1)
        self.assignment2 = Assignment(2, 2, 4, 1, 1)
        self.conflict = Conflict(
            conflict_type="teacher_time",
            assignments=[self.assignment1, self.assignment2],
            description="教师时间冲突",
            severity="high"
        )
    
    def test_conflict_creation(self):
        """测试冲突创建"""
        self.assertEqual(self.conflict.conflict_type, "teacher_time")
        self.assertEqual(len(self.conflict.assignments), 2)
        self.assertEqual(self.conflict.severity, "high")
    
    def test_invalid_conflict_assignments(self):
        """测试无效的冲突分配"""
        with self.assertRaises(ValueError):
            Conflict(
                conflict_type="teacher_time",
                assignments=[self.assignment1],  # 只有一个分配
                description="测试"
            )
    
    def test_conflict_key(self):
        """测试冲突键"""
        key = self.conflict.conflict_key
        self.assertIsInstance(key, str)
        self.assertIn("teacher_time", key)
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = self.conflict.to_dict()
        self.assertEqual(result['conflict_type'], "teacher_time")
        self.assertEqual(len(result['assignments']), 2)


class TestScheduleResult(unittest.TestCase):
    """测试ScheduleResult模型"""
    
    def setUp(self):
        """设置测试数据"""
        self.assignments = [
            Assignment(1, 2, 3, 1, 1),
            Assignment(2, 3, 4, 1, 2),
        ]
        self.conflicts = [
            Conflict("teacher_time", self.assignments, "测试冲突", "high")
        ]
        self.result = ScheduleResult(
            assignments=self.assignments,
            conflicts=self.conflicts,
            fitness_score=85.5,
            algorithm_used="genetic"
        )
    
    def test_schedule_result_creation(self):
        """测试排课结果创建"""
        self.assertEqual(len(self.result.assignments), 2)
        self.assertEqual(len(self.result.conflicts), 1)
        self.assertEqual(self.result.fitness_score, 85.5)
        self.assertEqual(self.result.algorithm_used, "genetic")
    
    def test_is_valid(self):
        """测试有效性检查"""
        # 有高严重性冲突，应该无效
        self.assertFalse(self.result.is_valid)
        
        # 创建无冲突的结果
        valid_result = ScheduleResult(
            assignments=self.assignments,
            conflicts=[],
            fitness_score=85.5
        )
        self.assertTrue(valid_result.is_valid)
    
    def test_total_assignments(self):
        """测试总分配数量"""
        self.assertEqual(self.result.total_assignments, 2)
    
    def test_conflict_count(self):
        """测试冲突数量"""
        self.assertEqual(self.result.conflict_count, 1)
    
    def test_high_severity_conflicts(self):
        """测试高严重性冲突"""
        high_conflicts = self.result.high_severity_conflicts
        self.assertEqual(len(high_conflicts), 1)
        self.assertEqual(high_conflicts[0].severity, "high")
    
    def test_get_assignments_by_teacher(self):
        """测试按教师获取分配"""
        teacher_assignments = self.result.get_assignments_by_teacher(2)
        self.assertEqual(len(teacher_assignments), 1)
        self.assertEqual(teacher_assignments[0].teacher_id, 2)
    
    def test_get_assignments_by_classroom(self):
        """测试按教室获取分配"""
        classroom_assignments = self.result.get_assignments_by_classroom(3)
        self.assertEqual(len(classroom_assignments), 1)
        self.assertEqual(classroom_assignments[0].classroom_id, 3)
    
    def test_get_assignments_by_time(self):
        """测试按时间获取分配"""
        time_assignments = self.result.get_assignments_by_time(1, 1)
        self.assertEqual(len(time_assignments), 1)
        self.assertEqual(time_assignments[0].day_of_week, 1)
        self.assertEqual(time_assignments[0].time_slot, 1)
    
    def test_to_dict(self):
        """测试转换为字典"""
        result_dict = self.result.to_dict()
        self.assertEqual(len(result_dict['assignments']), 2)
        self.assertEqual(len(result_dict['conflicts']), 1)
        self.assertEqual(result_dict['fitness_score'], 85.5)
        self.assertEqual(result_dict['algorithm_used'], "genetic")
        self.assertFalse(result_dict['is_valid'])
    
    def test_to_json(self):
        """测试转换为JSON"""
        json_str = self.result.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("genetic", json_str)


class TestTeacherPreference(unittest.TestCase):
    """测试TeacherPreference模型"""
    
    def test_teacher_preference_creation(self):
        """测试教师偏好创建"""
        pref = TeacherPreference(
            teacher_id=1,
            day_of_week=1,
            time_slot=1,
            preference_score=0.8,
            is_available=True,
            reason="偏好上午时间"
        )
        self.assertEqual(pref.teacher_id, 1)
        self.assertEqual(pref.preference_score, 0.8)
        self.assertTrue(pref.is_available)
    
    def test_invalid_preference_score(self):
        """测试无效的偏好分数"""
        with self.assertRaises(ValueError):
            TeacherPreference(1, 1, 1, 1.5)  # 超过1.0
        
        with self.assertRaises(ValueError):
            TeacherPreference(1, 1, 1, -0.1)  # 小于0.0


class TestCourseRequirement(unittest.TestCase):
    """测试CourseRequirement模型"""
    
    def test_course_requirement_creation(self):
        """测试课程需求创建"""
        req = CourseRequirement(
            course_id=1,
            required_sessions=3,
            session_duration=2,
            preferred_days=[1, 3, 5],
            preferred_times=[1, 2, 3],
            room_requirements={'type': 'lab', 'capacity': 30}
        )
        self.assertEqual(req.course_id, 1)
        self.assertEqual(req.required_sessions, 3)
        self.assertEqual(req.session_duration, 2)
        self.assertEqual(len(req.preferred_days), 3)
    
    def test_invalid_required_sessions(self):
        """测试无效的必需课时"""
        with self.assertRaises(ValueError):
            CourseRequirement(1, 0)  # 课时数为0
        
        with self.assertRaises(ValueError):
            CourseRequirement(1, -1)  # 负数课时
    
    def test_invalid_session_duration(self):
        """测试无效的课时长度"""
        with self.assertRaises(ValueError):
            CourseRequirement(1, 3, 0)  # 时长为0


if __name__ == '__main__':
    unittest.main()
