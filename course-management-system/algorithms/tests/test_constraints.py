# file: algorithms/tests/test_constraints.py
# 功能: 测试约束条件模块

import unittest
from ..models import Assignment, TeacherPreference
from ..constraints.hard_constraints import HardConstraints
from ..constraints.soft_constraints import SoftConstraints
from ..constraints.manager import ConstraintManager


class TestHardConstraints(unittest.TestCase):
    """测试硬约束条件"""
    
    def setUp(self):
        """设置测试数据"""
        self.assignment1 = Assignment(1, 1, 1, 1, 1)  # 课程1，教师1，教室1，周一第1节
        self.assignment2 = Assignment(2, 1, 2, 1, 1)  # 课程2，教师1，教室2，周一第1节
        self.assignment3 = Assignment(3, 2, 1, 1, 1)  # 课程3，教师2，教室1，周一第1节
        
        self.course_data = {
            'max_students': 30,
            'is_active': True,
            'is_published': True,
        }
        
        self.teacher_data = {
            'qualified_courses': [1, 2, 3],
            'max_daily_hours': 8,
        }
        
        self.classroom_data = {
            'capacity': 50,
            'is_available': True,
            'is_active': True,
        }
    
    def test_teacher_conflict_check_no_conflict(self):
        """测试教师无冲突情况"""
        existing = [self.assignment1]
        new_assignment = Assignment(2, 1, 2, 1, 2)  # 不同时间段
        
        result = HardConstraints.teacher_conflict_check(new_assignment, existing)
        self.assertTrue(result)
    
    def test_teacher_conflict_check_with_conflict(self):
        """测试教师有冲突情况"""
        existing = [self.assignment1]
        
        result = HardConstraints.teacher_conflict_check(self.assignment2, existing)
        self.assertFalse(result)
    
    def test_classroom_conflict_check_no_conflict(self):
        """测试教室无冲突情况"""
        existing = [self.assignment1]
        new_assignment = Assignment(2, 2, 1, 1, 2)  # 不同时间段
        
        result = HardConstraints.classroom_conflict_check(new_assignment, existing)
        self.assertTrue(result)
    
    def test_classroom_conflict_check_with_conflict(self):
        """测试教室有冲突情况"""
        existing = [self.assignment1]
        
        result = HardConstraints.classroom_conflict_check(self.assignment3, existing)
        self.assertFalse(result)
    
    def test_classroom_capacity_check_sufficient(self):
        """测试教室容量充足"""
        result = HardConstraints.classroom_capacity_check(
            self.assignment1, self.course_data, self.classroom_data
        )
        self.assertTrue(result)
    
    def test_classroom_capacity_check_insufficient(self):
        """测试教室容量不足"""
        insufficient_classroom = {'capacity': 20}
        
        result = HardConstraints.classroom_capacity_check(
            self.assignment1, self.course_data, insufficient_classroom
        )
        self.assertFalse(result)
    
    def test_teacher_qualification_check_qualified(self):
        """测试教师有资格"""
        result = HardConstraints.teacher_qualification_check(
            self.assignment1, self.teacher_data, self.course_data
        )
        self.assertTrue(result)
    
    def test_teacher_qualification_check_unqualified(self):
        """测试教师无资格"""
        unqualified_teacher = {'qualified_courses': [2, 3]}  # 不包含课程1
        
        result = HardConstraints.teacher_qualification_check(
            self.assignment1, unqualified_teacher, self.course_data
        )
        self.assertFalse(result)
    
    def test_time_slot_validity_check_valid(self):
        """测试有效时间段"""
        result = HardConstraints.time_slot_validity_check(self.assignment1)
        self.assertTrue(result)
    
    def test_time_slot_validity_check_invalid(self):
        """测试无效时间段"""
        invalid_assignment = Assignment(1, 1, 1, 1, 25)  # 无效时间段
        
        result = HardConstraints.time_slot_validity_check(invalid_assignment)
        self.assertFalse(result)
    
    def test_teacher_workload_check_within_limit(self):
        """测试教师工作量在限制内"""
        existing = [Assignment(2, 1, 2, 1, 2)]  # 教师1已有1节课
        
        result = HardConstraints.teacher_workload_check(
            self.assignment1, existing, self.teacher_data
        )
        self.assertTrue(result)
    
    def test_teacher_workload_check_exceeds_limit(self):
        """测试教师工作量超限"""
        # 创建8节课，再加1节就超限
        existing = [Assignment(i, 1, 1, 1, i) for i in range(2, 10)]
        
        result = HardConstraints.teacher_workload_check(
            self.assignment1, existing, self.teacher_data, max_hours_per_day=8
        )
        self.assertFalse(result)
    
    def test_check_all_hard_constraints(self):
        """测试检查所有硬约束"""
        existing = []
        
        results = HardConstraints.check_all_hard_constraints(
            self.assignment1, existing, self.course_data, 
            self.classroom_data, self.teacher_data
        )
        
        # 所有约束都应该通过
        for constraint, passed in results.items():
            self.assertTrue(passed, f"Constraint {constraint} failed")
    
    def test_is_valid_assignment(self):
        """测试分配有效性"""
        existing = []
        
        result = HardConstraints.is_valid_assignment(
            self.assignment1, existing, self.course_data,
            self.classroom_data, self.teacher_data
        )
        self.assertTrue(result)
    
    def test_get_violations(self):
        """测试获取违反的约束"""
        existing = [self.assignment1]  # 已有分配
        
        violations = HardConstraints.get_violations(
            self.assignment2, existing, self.course_data,
            self.classroom_data, self.teacher_data
        )
        
        self.assertIn('教师时间冲突', violations)


class TestSoftConstraints(unittest.TestCase):
    """测试软约束条件"""
    
    def setUp(self):
        """设置测试数据"""
        self.assignment = Assignment(1, 1, 1, 1, 2)  # 周一第2节
        self.existing = []
        
        self.teacher_preferences = {
            1: [TeacherPreference(1, 1, 2, 0.9, True, "偏好上午")]
        }
        
        self.teacher_data = {
            'max_weekly_hours': 16,
            'time_preferences': {
                '1': {'2': 0.9}  # 周一第2节偏好0.9
            }
        }
        
        self.classroom_data = {
            'capacity': 50,
            'room_type': 'lecture'
        }
        
        self.course_data = {
            'max_students': 30,
            'name': '计算机基础'
        }
    
    def test_teacher_preference_score_high(self):
        """测试高偏好时间段"""
        score = SoftConstraints.teacher_preference_score(
            self.assignment, self.teacher_preferences, self.teacher_data
        )
        self.assertGreater(score, 0.8)
    
    def test_teacher_preference_score_default(self):
        """测试默认偏好评分"""
        # 没有偏好数据时的默认评分
        score = SoftConstraints.teacher_preference_score(
            self.assignment, None, None
        )
        self.assertGreater(score, 0.0)
    
    def test_workload_balance_score_ideal(self):
        """测试理想工作量平衡"""
        score = SoftConstraints.workload_balance_score(
            self.assignment, self.existing, self.teacher_data
        )
        self.assertGreater(score, 0.0)
    
    def test_time_distribution_score_single(self):
        """测试单个课程时间分布"""
        score = SoftConstraints.time_distribution_score(
            self.assignment, self.existing
        )
        self.assertEqual(score, 1.0)  # 单个课程应该得满分
    
    def test_classroom_utilization_score_optimal(self):
        """测试最优教室利用率"""
        # 30人课程，50人教室，利用率60%，接近理想范围
        score = SoftConstraints.classroom_utilization_score(
            self.assignment, self.existing, self.classroom_data, self.course_data
        )
        self.assertGreater(score, 0.5)
    
    def test_day_balance_score_single(self):
        """测试单日课程平衡"""
        score = SoftConstraints.day_balance_score(
            self.assignment, self.existing
        )
        self.assertEqual(score, 1.0)  # 单个课程应该得满分
    
    def test_consecutive_classes_penalty_none(self):
        """测试无连续课程惩罚"""
        score = SoftConstraints.consecutive_classes_penalty(
            self.assignment, self.existing
        )
        self.assertEqual(score, 1.0)  # 无连续课程应该得满分
    
    def test_consecutive_classes_penalty_with_consecutive(self):
        """测试有连续课程的惩罚"""
        # 添加连续的课程
        consecutive_assignment = Assignment(2, 1, 1, 1, 3)  # 第3节课
        existing_with_consecutive = [consecutive_assignment]
        
        score = SoftConstraints.consecutive_classes_penalty(
            self.assignment, existing_with_consecutive
        )
        self.assertLessEqual(score, 1.0)
    
    def test_room_type_match_score_default(self):
        """测试教室类型匹配默认评分"""
        score = SoftConstraints.room_type_match_score(
            self.assignment, self.classroom_data, self.course_data
        )
        self.assertGreater(score, 0.0)
    
    def test_calculate_total_score(self):
        """测试计算总软约束评分"""
        score = SoftConstraints.calculate_total_score(
            self.assignment, self.existing, self.teacher_preferences,
            self.teacher_data, self.classroom_data, self.course_data
        )
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_calculate_total_score_with_weights(self):
        """测试使用自定义权重计算总评分"""
        weights = {
            'teacher_preference': 0.5,
            'workload_balance': 0.2,
            'time_distribution': 0.1,
            'classroom_utilization': 0.1,
            'day_balance': 0.05,
            'consecutive_penalty': 0.03,
            'room_type_match': 0.02,
        }
        
        score = SoftConstraints.calculate_total_score(
            self.assignment, self.existing, self.teacher_preferences,
            self.teacher_data, self.classroom_data, self.course_data, weights
        )
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestConstraintManager(unittest.TestCase):
    """测试约束管理器"""
    
    def setUp(self):
        """设置测试数据"""
        self.manager = ConstraintManager()
        
        self.courses = [
            {'id': 1, 'max_students': 30, 'is_active': True, 'is_published': True},
            {'id': 2, 'max_students': 25, 'is_active': True, 'is_published': True},
        ]
        
        self.teachers = [
            {'id': 1, 'qualified_courses': [1, 2], 'max_weekly_hours': 16},
            {'id': 2, 'qualified_courses': [2], 'max_weekly_hours': 12},
        ]
        
        self.classrooms = [
            {'id': 1, 'capacity': 50, 'is_available': True, 'is_active': True},
            {'id': 2, 'capacity': 30, 'is_available': True, 'is_active': True},
        ]
        
        self.manager.set_data_cache(self.courses, self.teachers, self.classrooms)
        
        self.assignment = Assignment(1, 1, 1, 1, 1)
        self.existing = []
    
    def test_check_hard_constraints_valid(self):
        """测试检查有效的硬约束"""
        result = self.manager.check_hard_constraints(self.assignment, self.existing)
        self.assertTrue(result)
    
    def test_check_hard_constraints_invalid(self):
        """测试检查无效的硬约束"""
        # 创建冲突的分配
        conflicting = Assignment(2, 1, 2, 1, 1)  # 同一教师同一时间
        existing_with_conflict = [self.assignment]
        
        result = self.manager.check_hard_constraints(conflicting, existing_with_conflict)
        self.assertFalse(result)
    
    def test_get_hard_constraint_violations(self):
        """测试获取硬约束违反"""
        conflicting = Assignment(2, 1, 2, 1, 1)
        existing_with_conflict = [self.assignment]
        
        violations = self.manager.get_hard_constraint_violations(
            conflicting, existing_with_conflict
        )
        
        self.assertIn('教师时间冲突', violations)
    
    def test_calculate_soft_score(self):
        """测试计算软约束评分"""
        score = self.manager.calculate_soft_score(self.assignment, self.existing)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_evaluate_assignment(self):
        """测试评估分配"""
        evaluation = self.manager.evaluate_assignment(self.assignment, self.existing)
        
        self.assertIn('assignment', evaluation)
        self.assertIn('hard_valid', evaluation)
        self.assertIn('soft_score', evaluation)
        self.assertIn('overall_score', evaluation)
        
        self.assertTrue(evaluation['hard_valid'])
        self.assertGreater(evaluation['overall_score'], 0)
    
    def test_evaluate_schedule(self):
        """测试评估整个排课方案"""
        assignments = [self.assignment]
        
        evaluation = self.manager.evaluate_schedule(assignments)
        
        self.assertIn('total_assignments', evaluation)
        self.assertIn('hard_violations', evaluation)
        self.assertIn('overall_fitness', evaluation)
        self.assertIn('is_valid', evaluation)
        
        self.assertEqual(evaluation['total_assignments'], 1)
        self.assertEqual(evaluation['hard_violations'], 0)
        self.assertTrue(evaluation['is_valid'])
    
    def test_find_conflicts(self):
        """测试查找冲突"""
        # 创建有冲突的分配
        assignments = [
            Assignment(1, 1, 1, 1, 1),
            Assignment(2, 1, 2, 1, 1),  # 教师时间冲突
        ]
        
        conflicts = self.manager.find_conflicts(assignments)
        
        self.assertGreater(len(conflicts), 0)
        self.assertEqual(conflicts[0].conflict_type, 'teacher_time')
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 先进行一些操作
        self.manager.check_hard_constraints(self.assignment, self.existing)
        self.manager.calculate_soft_score(self.assignment, self.existing)
        
        stats = self.manager.get_statistics()
        
        self.assertIn('total_checks', stats)
        self.assertIn('hard_violations', stats)
        self.assertIn('average_soft_score', stats)
        
        self.assertGreater(stats['total_checks'], 0)
    
    def test_reset_statistics(self):
        """测试重置统计信息"""
        # 先进行一些操作
        self.manager.check_hard_constraints(self.assignment, self.existing)
        
        # 重置统计
        self.manager.reset_statistics()
        
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total_checks'], 0)
    
    def test_update_soft_weights(self):
        """测试更新软约束权重"""
        new_weights = {'teacher_preference': 0.5}
        self.manager.update_soft_weights(new_weights)
        
        self.assertEqual(self.manager.soft_weights['teacher_preference'], 0.5)
    
    def test_validate_assignment_data(self):
        """测试验证分配数据"""
        errors = self.manager.validate_assignment_data(self.assignment)
        self.assertEqual(len(errors), 0)  # 应该没有错误
        
        # 测试无效数据
        invalid_assignment = Assignment(999, 999, 999, 1, 1)
        errors = self.manager.validate_assignment_data(invalid_assignment)
        self.assertGreater(len(errors), 0)  # 应该有错误


if __name__ == '__main__':
    unittest.main()
