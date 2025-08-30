# file: algorithms/genetic/individual.py
# 功能: 遗传算法个体表示

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import copy
import json
from ..models import Assignment
from ..constraints.manager import ConstraintManager


@dataclass
class Individual:
    """个体 - 代表一个完整的排课方案"""
    
    assignments: List[Assignment]
    fitness: float = field(default=0.0, init=False)
    hard_violations: int = field(default=0, init=False)
    soft_score: float = field(default=0.0, init=False)
    generation: int = field(default=0, init=False)
    
    # 缓存的评估结果
    _evaluated: bool = field(default=False, init=False, repr=False)
    _conflicts: List[Any] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.assignments:
            raise ValueError("Individual must have at least one assignment")
    
    def calculate_fitness(self, constraint_manager: ConstraintManager) -> float:
        """计算个体适应度"""
        if self._evaluated:
            return self.fitness
        
        # 评估整个排课方案
        evaluation = constraint_manager.evaluate_schedule(self.assignments)
        
        self.hard_violations = evaluation['hard_violations']
        self.soft_score = evaluation['average_soft_score']
        self._conflicts = evaluation['conflicts']
        
        # 计算适应度
        if self.hard_violations > 0:
            # 有硬约束违反，适应度为负值
            self.fitness = -self.hard_violations * 1000 - (100 - self.soft_score * 100)
        else:
            # 无硬约束违反，适应度为软约束得分
            self.fitness = self.soft_score * 100
        
        self._evaluated = True
        return self.fitness
    
    def is_valid(self) -> bool:
        """检查个体是否有效（无硬约束违反）"""
        return self.hard_violations == 0
    
    def get_conflicts(self) -> List[Any]:
        """获取冲突列表"""
        return self._conflicts.copy()
    
    def copy(self) -> 'Individual':
        """创建个体副本"""
        new_assignments = [assignment.copy() for assignment in self.assignments]
        new_individual = Individual(assignments=new_assignments)
        new_individual.generation = self.generation
        return new_individual
    
    def deep_copy(self) -> 'Individual':
        """创建深度副本"""
        return copy.deepcopy(self)
    
    def get_assignment_by_course(self, course_id: int) -> Optional[Assignment]:
        """根据课程ID获取分配"""
        for assignment in self.assignments:
            if assignment.course_id == course_id:
                return assignment
        return None
    
    def get_assignments_by_teacher(self, teacher_id: int) -> List[Assignment]:
        """根据教师ID获取所有分配"""
        return [a for a in self.assignments if a.teacher_id == teacher_id]
    
    def get_assignments_by_classroom(self, classroom_id: int) -> List[Assignment]:
        """根据教室ID获取所有分配"""
        return [a for a in self.assignments if a.classroom_id == classroom_id]
    
    def get_assignments_by_time(self, day_of_week: int, time_slot: int) -> List[Assignment]:
        """根据时间获取所有分配"""
        return [a for a in self.assignments 
                if a.day_of_week == day_of_week and a.time_slot == time_slot]
    
    def replace_assignment(self, old_assignment: Assignment, new_assignment: Assignment):
        """替换分配"""
        for i, assignment in enumerate(self.assignments):
            if assignment == old_assignment:
                self.assignments[i] = new_assignment
                self._evaluated = False  # 标记需要重新评估
                break
    
    def remove_assignment(self, assignment: Assignment):
        """移除分配"""
        if assignment in self.assignments:
            self.assignments.remove(assignment)
            self._evaluated = False
    
    def add_assignment(self, assignment: Assignment):
        """添加分配"""
        self.assignments.append(assignment)
        self._evaluated = False
    
    def get_teacher_workload(self) -> Dict[int, int]:
        """获取每个教师的工作量"""
        workload = {}
        for assignment in self.assignments:
            teacher_id = assignment.teacher_id
            workload[teacher_id] = workload.get(teacher_id, 0) + 1
        return workload
    
    def get_classroom_utilization(self) -> Dict[int, int]:
        """获取每个教室的使用次数"""
        utilization = {}
        for assignment in self.assignments:
            classroom_id = assignment.classroom_id
            utilization[classroom_id] = utilization.get(classroom_id, 0) + 1
        return utilization
    
    def get_time_distribution(self) -> Dict[tuple, int]:
        """获取时间分布"""
        distribution = {}
        for assignment in self.assignments:
            time_key = (assignment.day_of_week, assignment.time_slot)
            distribution[time_key] = distribution.get(time_key, 0) + 1
        return distribution
    
    def validate_structure(self) -> List[str]:
        """验证个体结构的完整性"""
        errors = []
        
        if not self.assignments:
            errors.append("Individual has no assignments")
            return errors
        
        # 检查分配的唯一性（同一课程不应有多个分配）
        course_ids = [a.course_id for a in self.assignments]
        if len(course_ids) != len(set(course_ids)):
            errors.append("Duplicate course assignments found")
        
        # 检查分配数据的有效性
        for i, assignment in enumerate(self.assignments):
            try:
                # 验证时间范围
                if not (1 <= assignment.day_of_week <= 7):
                    errors.append(f"Assignment {i}: Invalid day_of_week {assignment.day_of_week}")
                
                if not (1 <= assignment.time_slot <= 20):
                    errors.append(f"Assignment {i}: Invalid time_slot {assignment.time_slot}")
                
                # 验证ID的有效性
                if assignment.course_id <= 0:
                    errors.append(f"Assignment {i}: Invalid course_id {assignment.course_id}")
                
                if assignment.teacher_id <= 0:
                    errors.append(f"Assignment {i}: Invalid teacher_id {assignment.teacher_id}")
                
                if assignment.classroom_id <= 0:
                    errors.append(f"Assignment {i}: Invalid classroom_id {assignment.classroom_id}")
                    
            except Exception as e:
                errors.append(f"Assignment {i}: Validation error - {str(e)}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'assignments': [a.to_dict() for a in self.assignments],
            'fitness': self.fitness,
            'hard_violations': self.hard_violations,
            'soft_score': self.soft_score,
            'generation': self.generation,
            'is_valid': self.is_valid(),
            'total_assignments': len(self.assignments),
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_assignments(cls, assignments: List[Assignment]) -> 'Individual':
        """从分配列表创建个体"""
        return cls(assignments=assignments.copy())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Individual':
        """从字典创建个体"""
        assignments = [Assignment.from_dict(a) for a in data['assignments']]
        individual = cls(assignments=assignments)
        individual.fitness = data.get('fitness', 0.0)
        individual.hard_violations = data.get('hard_violations', 0)
        individual.soft_score = data.get('soft_score', 0.0)
        individual.generation = data.get('generation', 0)
        return individual
    
    def __len__(self) -> int:
        """返回分配数量"""
        return len(self.assignments)
    
    def __getitem__(self, index: int) -> Assignment:
        """支持索引访问"""
        return self.assignments[index]
    
    def __setitem__(self, index: int, assignment: Assignment):
        """支持索引赋值"""
        self.assignments[index] = assignment
        self._evaluated = False
    
    def __iter__(self):
        """支持迭代"""
        return iter(self.assignments)
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, Individual):
            return False
        return self.assignments == other.assignments
    
    def __hash__(self) -> int:
        """哈希值计算"""
        return hash(tuple(
            (a.course_id, a.teacher_id, a.classroom_id, a.day_of_week, a.time_slot)
            for a in self.assignments
        ))
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Individual(assignments={len(self.assignments)}, fitness={self.fitness:.2f}, valid={self.is_valid()})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Individual(assignments={len(self.assignments)}, fitness={self.fitness:.2f}, hard_violations={self.hard_violations}, soft_score={self.soft_score:.2f})"
