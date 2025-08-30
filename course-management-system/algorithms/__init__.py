# file: algorithms/__init__.py
# 功能: 智能排课算法模块初始化

"""
智能排课算法模块

本模块提供完整的智能排课算法解决方案，包括：
- 约束条件定义和检查
- 遗传算法排课器
- 启发式算法排课器
- 冲突检测与解决
- 性能优化
- 统一的排课引擎接口
"""

__version__ = '1.0.0'
__author__ = 'Course Management System Team'

from .models import Assignment, Conflict, ScheduleResult
from .constraints import HardConstraints, SoftConstraints, ConstraintManager
from .genetic import Individual, GeneticAlgorithm
from .heuristic import GreedyScheduler
from .conflict import ConflictDetector, ConflictResolver
from .optimizer import ScheduleOptimizer
from .engine import SchedulingEngine

__all__ = [
    'Assignment',
    'Conflict', 
    'ScheduleResult',
    'HardConstraints',
    'SoftConstraints',
    'ConstraintManager',
    'Individual',
    'GeneticAlgorithm',
    'GreedyScheduler',
    'ConflictDetector',
    'ConflictResolver',
    'ScheduleOptimizer',
    'SchedulingEngine',
]
