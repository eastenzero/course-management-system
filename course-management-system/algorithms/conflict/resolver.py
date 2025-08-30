# file: algorithms/conflict/resolver.py
# 功能: 冲突解决器

import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from ..models import Assignment, Conflict
from ..constraints.manager import ConstraintManager

logger = logging.getLogger(__name__)


class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self, constraint_manager: Optional[ConstraintManager] = None,
                 max_attempts_per_conflict: int = 50,
                 resolution_strategies: List[str] = None):
        """
        初始化冲突解决器
        
        Args:
            constraint_manager: 约束管理器
            max_attempts_per_conflict: 每个冲突的最大解决尝试次数
            resolution_strategies: 解决策略列表
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        self.max_attempts_per_conflict = max_attempts_per_conflict
        
        if resolution_strategies is None:
            self.resolution_strategies = [
                'time_reassignment',
                'classroom_reassignment', 
                'teacher_reassignment',
                'swap_assignments',
                'split_assignment',
            ]
        else:
            self.resolution_strategies = resolution_strategies
        
        # 统计信息
        self.stats = {
            'conflicts_resolved': 0,
            'conflicts_failed': 0,
            'total_attempts': 0,
            'strategy_success': {strategy: 0 for strategy in self.resolution_strategies},
            'strategy_attempts': {strategy: 0 for strategy in self.resolution_strategies},
        }
    
    def resolve_conflicts(self, assignments: List[Assignment], conflicts: List[Conflict],
                         teachers: List[Dict], classrooms: List[Dict]) -> Tuple[List[Assignment], List[Conflict]]:
        """解决冲突列表"""
        resolved_assignments = [a.copy() for a in assignments]
        unresolved_conflicts = []
        
        logger.info(f"Starting conflict resolution for {len(conflicts)} conflicts")
        
        # 按严重性排序冲突（高严重性优先）
        sorted_conflicts = sorted(conflicts, key=lambda c: {'high': 3, 'medium': 2, 'low': 1}[c.severity], reverse=True)
        
        for conflict in sorted_conflicts:
            success = self._resolve_single_conflict(conflict, resolved_assignments, teachers, classrooms)
            
            if success:
                self.stats['conflicts_resolved'] += 1
                logger.debug(f"Resolved conflict: {conflict.conflict_type}")
            else:
                self.stats['conflicts_failed'] += 1
                unresolved_conflicts.append(conflict)
                logger.warning(f"Failed to resolve conflict: {conflict.conflict_type}")
        
        logger.info(f"Conflict resolution completed: {self.stats['conflicts_resolved']} resolved, "
                   f"{len(unresolved_conflicts)} unresolved")
        
        return resolved_assignments, unresolved_conflicts
    
    def _resolve_single_conflict(self, conflict: Conflict, assignments: List[Assignment],
                               teachers: List[Dict], classrooms: List[Dict]) -> bool:
        """解决单个冲突"""
        for strategy in self.resolution_strategies:
            self.stats['strategy_attempts'][strategy] += 1
            
            if strategy == 'time_reassignment':
                success = self._resolve_by_time_reassignment(conflict, assignments)
            elif strategy == 'classroom_reassignment':
                success = self._resolve_by_classroom_reassignment(conflict, assignments, classrooms)
            elif strategy == 'teacher_reassignment':
                success = self._resolve_by_teacher_reassignment(conflict, assignments, teachers)
            elif strategy == 'swap_assignments':
                success = self._resolve_by_swap_assignments(conflict, assignments)
            elif strategy == 'split_assignment':
                success = self._resolve_by_split_assignment(conflict, assignments)
            else:
                success = False
            
            if success:
                self.stats['strategy_success'][strategy] += 1
                return True
        
        return False
    
    def _resolve_by_time_reassignment(self, conflict: Conflict, assignments: List[Assignment]) -> bool:
        """通过重新分配时间解决冲突"""
        if conflict.conflict_type not in ['teacher_time', 'classroom_time', 'student_course']:
            return False
        
        # 选择一个冲突的分配进行时间调整
        conflicting_assignment = random.choice(conflict.assignments)
        
        # 在assignments中找到对应的分配
        assignment_index = None
        for i, assignment in enumerate(assignments):
            if (assignment.course_id == conflicting_assignment.course_id and
                assignment.teacher_id == conflicting_assignment.teacher_id and
                assignment.classroom_id == conflicting_assignment.classroom_id):
                assignment_index = i
                break
        
        if assignment_index is None:
            return False
        
        original_assignment = assignments[assignment_index]
        
        # 尝试新的时间段
        for attempt in range(self.max_attempts_per_conflict):
            self.stats['total_attempts'] += 1
            
            new_day = random.randint(1, 5)  # 周一到周五
            new_time_slot = random.randint(1, 10)  # 10个时间段
            
            # 创建新的分配
            new_assignment = original_assignment.copy()
            new_assignment.day_of_week = new_day
            new_assignment.time_slot = new_time_slot
            
            # 检查新分配是否有效
            temp_assignments = assignments.copy()
            temp_assignments[assignment_index] = new_assignment
            
            if self.constraint_manager.check_hard_constraints(new_assignment, 
                                                            temp_assignments[:assignment_index] + temp_assignments[assignment_index+1:]):
                assignments[assignment_index] = new_assignment
                return True
        
        return False
    
    def _resolve_by_classroom_reassignment(self, conflict: Conflict, assignments: List[Assignment],
                                         classrooms: List[Dict]) -> bool:
        """通过重新分配教室解决冲突"""
        if conflict.conflict_type != 'classroom_time':
            return False
        
        # 选择一个冲突的分配进行教室调整
        conflicting_assignment = random.choice(conflict.assignments)
        
        # 在assignments中找到对应的分配
        assignment_index = None
        for i, assignment in enumerate(assignments):
            if (assignment.course_id == conflicting_assignment.course_id and
                assignment.teacher_id == conflicting_assignment.teacher_id and
                assignment.day_of_week == conflicting_assignment.day_of_week and
                assignment.time_slot == conflicting_assignment.time_slot):
                assignment_index = i
                break
        
        if assignment_index is None:
            return False
        
        original_assignment = assignments[assignment_index]
        
        # 尝试其他教室
        available_classrooms = [c for c in classrooms 
                              if c['id'] != original_assignment.classroom_id]
        random.shuffle(available_classrooms)
        
        for classroom in available_classrooms:
            self.stats['total_attempts'] += 1
            
            # 创建新的分配
            new_assignment = original_assignment.copy()
            new_assignment.classroom_id = classroom['id']
            
            # 检查新分配是否有效
            temp_assignments = assignments.copy()
            temp_assignments[assignment_index] = new_assignment
            
            if self.constraint_manager.check_hard_constraints(new_assignment,
                                                            temp_assignments[:assignment_index] + temp_assignments[assignment_index+1:]):
                assignments[assignment_index] = new_assignment
                return True
        
        return False
    
    def _resolve_by_teacher_reassignment(self, conflict: Conflict, assignments: List[Assignment],
                                       teachers: List[Dict]) -> bool:
        """通过重新分配教师解决冲突"""
        if conflict.conflict_type != 'teacher_time':
            return False
        
        # 选择一个冲突的分配进行教师调整
        conflicting_assignment = random.choice(conflict.assignments)
        
        # 在assignments中找到对应的分配
        assignment_index = None
        for i, assignment in enumerate(assignments):
            if (assignment.course_id == conflicting_assignment.course_id and
                assignment.classroom_id == conflicting_assignment.classroom_id and
                assignment.day_of_week == conflicting_assignment.day_of_week and
                assignment.time_slot == conflicting_assignment.time_slot):
                assignment_index = i
                break
        
        if assignment_index is None:
            return False
        
        original_assignment = assignments[assignment_index]
        
        # 找到合格的其他教师
        qualified_teachers = [t for t in teachers 
                            if (t['id'] != original_assignment.teacher_id and
                                original_assignment.course_id in t.get('qualified_courses', []))]
        
        if not qualified_teachers:
            # 如果没有合格教师，尝试所有其他教师
            qualified_teachers = [t for t in teachers if t['id'] != original_assignment.teacher_id]
        
        random.shuffle(qualified_teachers)
        
        for teacher in qualified_teachers:
            self.stats['total_attempts'] += 1
            
            # 创建新的分配
            new_assignment = original_assignment.copy()
            new_assignment.teacher_id = teacher['id']
            
            # 检查新分配是否有效
            temp_assignments = assignments.copy()
            temp_assignments[assignment_index] = new_assignment
            
            if self.constraint_manager.check_hard_constraints(new_assignment,
                                                            temp_assignments[:assignment_index] + temp_assignments[assignment_index+1:]):
                assignments[assignment_index] = new_assignment
                return True
        
        return False
    
    def _resolve_by_swap_assignments(self, conflict: Conflict, assignments: List[Assignment]) -> bool:
        """通过交换分配解决冲突"""
        if len(conflict.assignments) < 2:
            return False
        
        # 选择两个冲突的分配
        assignment1, assignment2 = conflict.assignments[:2]
        
        # 在assignments中找到对应的分配
        index1 = index2 = None
        for i, assignment in enumerate(assignments):
            if (assignment.course_id == assignment1.course_id and
                assignment.teacher_id == assignment1.teacher_id):
                index1 = i
            elif (assignment.course_id == assignment2.course_id and
                  assignment.teacher_id == assignment2.teacher_id):
                index2 = i
        
        if index1 is None or index2 is None:
            return False
        
        # 尝试交换时间
        self.stats['total_attempts'] += 1
        
        temp_assignments = assignments.copy()
        
        # 交换时间信息
        temp_assignments[index1].day_of_week, temp_assignments[index2].day_of_week = \
            temp_assignments[index2].day_of_week, temp_assignments[index1].day_of_week
        temp_assignments[index1].time_slot, temp_assignments[index2].time_slot = \
            temp_assignments[index2].time_slot, temp_assignments[index1].time_slot
        
        # 检查交换后是否有效
        valid1 = self.constraint_manager.check_hard_constraints(
            temp_assignments[index1], 
            temp_assignments[:index1] + temp_assignments[index1+1:]
        )
        valid2 = self.constraint_manager.check_hard_constraints(
            temp_assignments[index2], 
            temp_assignments[:index2] + temp_assignments[index2+1:]
        )
        
        if valid1 and valid2:
            assignments[index1] = temp_assignments[index1]
            assignments[index2] = temp_assignments[index2]
            return True
        
        return False
    
    def _resolve_by_split_assignment(self, conflict: Conflict, assignments: List[Assignment]) -> bool:
        """通过拆分分配解决冲突（暂时不实现）"""
        # 这个策略比较复杂，需要将一个课程分配拆分成多个时间段
        # 暂时返回False
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_strategy_attempts = sum(self.stats['strategy_attempts'].values())
        total_strategy_success = sum(self.stats['strategy_success'].values())
        
        strategy_success_rates = {}
        for strategy in self.resolution_strategies:
            attempts = self.stats['strategy_attempts'][strategy]
            success = self.stats['strategy_success'][strategy]
            strategy_success_rates[strategy] = success / attempts if attempts > 0 else 0.0
        
        return {
            'conflicts_resolved': self.stats['conflicts_resolved'],
            'conflicts_failed': self.stats['conflicts_failed'],
            'total_attempts': self.stats['total_attempts'],
            'overall_success_rate': (self.stats['conflicts_resolved'] / 
                                   (self.stats['conflicts_resolved'] + self.stats['conflicts_failed'])
                                   if (self.stats['conflicts_resolved'] + self.stats['conflicts_failed']) > 0 else 0.0),
            'strategy_attempts': self.stats['strategy_attempts'].copy(),
            'strategy_success': self.stats['strategy_success'].copy(),
            'strategy_success_rates': strategy_success_rates,
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'conflicts_resolved': 0,
            'conflicts_failed': 0,
            'total_attempts': 0,
            'strategy_success': {strategy: 0 for strategy in self.resolution_strategies},
            'strategy_attempts': {strategy: 0 for strategy in self.resolution_strategies},
        }
