# file: algorithms/models.py
# 功能: 排课算法数据模型定义

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class Assignment:
    """课程分配模型 - 表示一个具体的课程安排"""
    
    course_id: int
    teacher_id: int
    classroom_id: int
    day_of_week: int  # 1-7 (周一到周日)
    time_slot: int    # 时间段编号
    semester: str = ""
    academic_year: str = ""
    week_range: str = "1-16"
    
    # 缓存的对象引用，用于提高性能
    _course: Optional[Any] = field(default=None, init=False, repr=False)
    _teacher: Optional[Any] = field(default=None, init=False, repr=False)
    _classroom: Optional[Any] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """初始化后验证"""
        if not (1 <= self.day_of_week <= 7):
            raise ValueError("day_of_week must be between 1 and 7")
        if not (1 <= self.time_slot <= 20):
            raise ValueError("time_slot must be between 1 and 20")
    
    @property
    def time_key(self) -> tuple:
        """时间键，用于冲突检测"""
        return (self.day_of_week, self.time_slot)
    
    @property
    def teacher_time_key(self) -> tuple:
        """教师时间键"""
        return (self.teacher_id, self.day_of_week, self.time_slot)
    
    @property
    def classroom_time_key(self) -> tuple:
        """教室时间键"""
        return (self.classroom_id, self.day_of_week, self.time_slot)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'course_id': self.course_id,
            'teacher_id': self.teacher_id,
            'classroom_id': self.classroom_id,
            'day_of_week': self.day_of_week,
            'time_slot': self.time_slot,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'week_range': self.week_range,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Assignment':
        """从字典创建"""
        return cls(**data)
    
    def copy(self) -> 'Assignment':
        """创建副本"""
        return Assignment(
            course_id=self.course_id,
            teacher_id=self.teacher_id,
            classroom_id=self.classroom_id,
            day_of_week=self.day_of_week,
            time_slot=self.time_slot,
            semester=self.semester,
            academic_year=self.academic_year,
            week_range=self.week_range,
        )


@dataclass
class Conflict:
    """冲突模型 - 表示排课冲突"""
    
    conflict_type: str  # 冲突类型：teacher_time, classroom_time, student_course等
    assignments: List[Assignment]
    description: str
    severity: str = "high"  # high, medium, low
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """初始化后验证"""
        if len(self.assignments) < 2:
            raise ValueError("Conflict must involve at least 2 assignments")
    
    @property
    def conflict_key(self) -> str:
        """冲突键，用于去重"""
        assignment_keys = sorted([
            f"{a.course_id}-{a.teacher_id}-{a.classroom_id}-{a.day_of_week}-{a.time_slot}"
            for a in self.assignments
        ])
        return f"{self.conflict_type}:{':'.join(assignment_keys)}"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'conflict_type': self.conflict_type,
            'assignments': [a.to_dict() for a in self.assignments],
            'description': self.description,
            'severity': self.severity,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class ScheduleResult:
    """排课结果模型"""
    
    assignments: List[Assignment]
    conflicts: List[Conflict] = field(default_factory=list)
    fitness_score: float = 0.0
    algorithm_used: str = ""
    generation_time: float = 0.0  # 生成时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_valid(self) -> bool:
        """是否为有效的排课方案（无硬约束冲突）"""
        return len([c for c in self.conflicts if c.severity == "high"]) == 0
    
    @property
    def total_assignments(self) -> int:
        """总分配数量"""
        return len(self.assignments)
    
    @property
    def conflict_count(self) -> int:
        """冲突数量"""
        return len(self.conflicts)
    
    @property
    def high_severity_conflicts(self) -> List[Conflict]:
        """高严重性冲突"""
        return [c for c in self.conflicts if c.severity == "high"]
    
    def get_assignments_by_teacher(self, teacher_id: int) -> List[Assignment]:
        """获取指定教师的所有分配"""
        return [a for a in self.assignments if a.teacher_id == teacher_id]
    
    def get_assignments_by_classroom(self, classroom_id: int) -> List[Assignment]:
        """获取指定教室的所有分配"""
        return [a for a in self.assignments if a.classroom_id == classroom_id]
    
    def get_assignments_by_time(self, day_of_week: int, time_slot: int) -> List[Assignment]:
        """获取指定时间的所有分配"""
        return [a for a in self.assignments 
                if a.day_of_week == day_of_week and a.time_slot == time_slot]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'assignments': [a.to_dict() for a in self.assignments],
            'conflicts': [c.to_dict() for c in self.conflicts],
            'fitness_score': self.fitness_score,
            'algorithm_used': self.algorithm_used,
            'generation_time': self.generation_time,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'is_valid': self.is_valid,
            'total_assignments': self.total_assignments,
            'conflict_count': self.conflict_count,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class TeacherPreference:
    """教师偏好模型"""
    
    teacher_id: int
    day_of_week: int
    time_slot: int
    preference_score: float  # 0.0-1.0，1.0表示最喜欢
    is_available: bool = True
    reason: str = ""
    
    def __post_init__(self):
        """初始化后验证"""
        if not (0.0 <= self.preference_score <= 1.0):
            raise ValueError("preference_score must be between 0.0 and 1.0")
        if not (1 <= self.day_of_week <= 7):
            raise ValueError("day_of_week must be between 1 and 7")
        if not (1 <= self.time_slot <= 20):
            raise ValueError("time_slot must be between 1 and 20")


@dataclass
class CourseRequirement:
    """课程需求模型"""
    
    course_id: int
    required_sessions: int  # 每周需要的课时数
    session_duration: int = 1  # 每次课的时长（时间段数）
    preferred_days: List[int] = field(default_factory=list)  # 偏好的星期
    preferred_times: List[int] = field(default_factory=list)  # 偏好的时间段
    room_requirements: Dict[str, Any] = field(default_factory=dict)  # 教室要求
    
    def __post_init__(self):
        """初始化后验证"""
        if self.required_sessions <= 0:
            raise ValueError("required_sessions must be positive")
        if self.session_duration <= 0:
            raise ValueError("session_duration must be positive")
