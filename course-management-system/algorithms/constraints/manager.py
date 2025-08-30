# file: algorithms/constraints/manager.py
# 功能: 约束管理器 - 统一管理硬约束和软约束

from typing import List, Dict, Any, Optional
from ..models import Assignment, Conflict, TeacherPreference
from .hard_constraints import HardConstraints
from .soft_constraints import SoftConstraints
import logging

logger = logging.getLogger(__name__)


class ConstraintManager:
    """约束管理器 - 统一管理硬约束和软约束检查"""
    
    def __init__(self, soft_constraint_weights: Dict[str, float] = None):
        """
        初始化约束管理器
        
        Args:
            soft_constraint_weights: 软约束权重配置
        """
        self.hard_constraints = HardConstraints()
        self.soft_constraints = SoftConstraints()
        
        # 默认软约束权重
        self.soft_weights = soft_constraint_weights or {
            'teacher_preference': 0.25,
            'workload_balance': 0.20,
            'time_distribution': 0.15,
            'classroom_utilization': 0.15,
            'day_balance': 0.10,
            'consecutive_penalty': 0.10,
            'room_type_match': 0.05,
        }
        
        # 数据缓存
        self.course_data_cache = {}
        self.teacher_data_cache = {}
        self.classroom_data_cache = {}
        self.teacher_preferences_cache = {}
        
        # 统计信息
        self.stats = {
            'total_checks': 0,
            'hard_violations': 0,
            'soft_scores': [],
        }
    
    def set_data_cache(self, courses: List[Dict] = None, teachers: List[Dict] = None,
                      classrooms: List[Dict] = None, 
                      teacher_preferences: List[TeacherPreference] = None):
        """设置数据缓存以提高性能"""
        if courses:
            self.course_data_cache = {c['id']: c for c in courses}
        
        if teachers:
            self.teacher_data_cache = {t['id']: t for t in teachers}
        
        if classrooms:
            self.classroom_data_cache = {c['id']: c for c in classrooms}
        
        if teacher_preferences:
            # 按教师ID分组偏好数据
            self.teacher_preferences_cache = {}
            for pref in teacher_preferences:
                teacher_id = pref.teacher_id
                if teacher_id not in self.teacher_preferences_cache:
                    self.teacher_preferences_cache[teacher_id] = []
                self.teacher_preferences_cache[teacher_id].append(pref)
    
    def check_hard_constraints(self, assignment: Assignment, 
                             existing_assignments: List[Assignment]) -> bool:
        """检查硬约束条件"""
        self.stats['total_checks'] += 1
        
        course_data = self.course_data_cache.get(assignment.course_id)
        teacher_data = self.teacher_data_cache.get(assignment.teacher_id)
        classroom_data = self.classroom_data_cache.get(assignment.classroom_id)
        
        is_valid = self.hard_constraints.is_valid_assignment(
            assignment, existing_assignments, course_data, classroom_data, teacher_data
        )
        
        if not is_valid:
            self.stats['hard_violations'] += 1
        
        return is_valid
    
    def get_hard_constraint_violations(self, assignment: Assignment,
                                     existing_assignments: List[Assignment]) -> List[str]:
        """获取硬约束违反列表"""
        course_data = self.course_data_cache.get(assignment.course_id)
        teacher_data = self.teacher_data_cache.get(assignment.teacher_id)
        classroom_data = self.classroom_data_cache.get(assignment.classroom_id)
        
        return self.hard_constraints.get_violations(
            assignment, existing_assignments, course_data, classroom_data, teacher_data
        )
    
    def calculate_soft_score(self, assignment: Assignment,
                           existing_assignments: List[Assignment]) -> float:
        """计算软约束评分"""
        course_data = self.course_data_cache.get(assignment.course_id)
        teacher_data = self.teacher_data_cache.get(assignment.teacher_id)
        classroom_data = self.classroom_data_cache.get(assignment.classroom_id)
        teacher_preferences = self.teacher_preferences_cache.get(assignment.teacher_id, [])
        
        score = self.soft_constraints.calculate_total_score(
            assignment, existing_assignments, 
            {assignment.teacher_id: teacher_preferences} if teacher_preferences else None,
            teacher_data, classroom_data, course_data, self.soft_weights
        )
        
        self.stats['soft_scores'].append(score)
        return score
    
    def evaluate_assignment(self, assignment: Assignment,
                          existing_assignments: List[Assignment]) -> Dict[str, Any]:
        """全面评估一个分配"""
        # 检查硬约束
        hard_valid = self.check_hard_constraints(assignment, existing_assignments)
        hard_violations = []
        
        if not hard_valid:
            hard_violations = self.get_hard_constraint_violations(assignment, existing_assignments)
        
        # 计算软约束评分
        soft_score = self.calculate_soft_score(assignment, existing_assignments)
        
        return {
            'assignment': assignment,
            'hard_valid': hard_valid,
            'hard_violations': hard_violations,
            'soft_score': soft_score,
            'overall_score': soft_score if hard_valid else -1000,  # 硬约束违反时给予极低分
        }
    
    def evaluate_schedule(self, assignments: List[Assignment]) -> Dict[str, Any]:
        """评估整个排课方案"""
        total_assignments = len(assignments)
        hard_violations = 0
        soft_scores = []
        conflicts = []
        
        # 逐个检查每个分配
        for i, assignment in enumerate(assignments):
            existing = assignments[:i]  # 之前的分配
            
            evaluation = self.evaluate_assignment(assignment, existing)
            
            if not evaluation['hard_valid']:
                hard_violations += 1
                # 创建冲突记录
                conflict = Conflict(
                    conflict_type='hard_constraint_violation',
                    assignments=[assignment],
                    description=f"硬约束违反: {', '.join(evaluation['hard_violations'])}",
                    severity='high'
                )
                conflicts.append(conflict)
            
            soft_scores.append(evaluation['soft_score'])
        
        # 计算总体评分
        if hard_violations > 0:
            overall_fitness = -hard_violations * 1000  # 硬约束违反的惩罚
        else:
            overall_fitness = sum(soft_scores) / len(soft_scores) if soft_scores else 0
        
        return {
            'total_assignments': total_assignments,
            'hard_violations': hard_violations,
            'hard_violation_rate': hard_violations / total_assignments if total_assignments > 0 else 0,
            'average_soft_score': sum(soft_scores) / len(soft_scores) if soft_scores else 0,
            'overall_fitness': overall_fitness,
            'conflicts': conflicts,
            'is_valid': hard_violations == 0,
        }
    
    def find_conflicts(self, assignments: List[Assignment]) -> List[Conflict]:
        """查找排课方案中的所有冲突"""
        conflicts = []
        
        # 教师时间冲突检测
        teacher_time_map = {}
        for assignment in assignments:
            key = assignment.teacher_time_key
            if key in teacher_time_map:
                conflict = Conflict(
                    conflict_type='teacher_time',
                    assignments=[teacher_time_map[key], assignment],
                    description=f"教师 {assignment.teacher_id} 在 周{assignment.day_of_week} 第{assignment.time_slot}节 有时间冲突",
                    severity='high'
                )
                conflicts.append(conflict)
            else:
                teacher_time_map[key] = assignment
        
        # 教室时间冲突检测
        classroom_time_map = {}
        for assignment in assignments:
            key = assignment.classroom_time_key
            if key in classroom_time_map:
                conflict = Conflict(
                    conflict_type='classroom_time',
                    assignments=[classroom_time_map[key], assignment],
                    description=f"教室 {assignment.classroom_id} 在 周{assignment.day_of_week} 第{assignment.time_slot}节 有时间冲突",
                    severity='high'
                )
                conflicts.append(conflict)
            else:
                classroom_time_map[key] = assignment
        
        return conflicts
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取约束检查统计信息"""
        avg_soft_score = (sum(self.stats['soft_scores']) / len(self.stats['soft_scores']) 
                         if self.stats['soft_scores'] else 0)
        
        return {
            'total_checks': self.stats['total_checks'],
            'hard_violations': self.stats['hard_violations'],
            'hard_violation_rate': (self.stats['hard_violations'] / self.stats['total_checks'] 
                                  if self.stats['total_checks'] > 0 else 0),
            'average_soft_score': avg_soft_score,
            'soft_score_count': len(self.stats['soft_scores']),
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'total_checks': 0,
            'hard_violations': 0,
            'soft_scores': [],
        }
    
    def update_soft_weights(self, new_weights: Dict[str, float]):
        """更新软约束权重"""
        self.soft_weights.update(new_weights)
        logger.info(f"Updated soft constraint weights: {self.soft_weights}")
    
    def validate_assignment_data(self, assignment: Assignment) -> List[str]:
        """验证分配数据的完整性"""
        errors = []
        
        if assignment.course_id not in self.course_data_cache:
            errors.append(f"Course {assignment.course_id} not found in cache")
        
        if assignment.teacher_id not in self.teacher_data_cache:
            errors.append(f"Teacher {assignment.teacher_id} not found in cache")
        
        if assignment.classroom_id not in self.classroom_data_cache:
            errors.append(f"Classroom {assignment.classroom_id} not found in cache")
        
        return errors
