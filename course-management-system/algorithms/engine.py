# file: algorithms/engine.py
# 功能: 统一的排课引擎 - 集成所有算法模块

import time
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from .models import Assignment, ScheduleResult, TeacherPreference
from .constraints.manager import ConstraintManager
from .genetic.genetic_algorithm import GeneticAlgorithm
from .heuristic.greedy_scheduler import GreedyScheduler
from .conflict.detector import ConflictDetector
from .conflict.resolver import ConflictResolver
from .conflict.analyzer import ConflictAnalyzer
from .optimizer.schedule_optimizer import ScheduleOptimizer
from .optimizer.parallel_ga import ParallelGeneticAlgorithm
from .optimizer.hybrid_optimizer import HybridOptimizer

logger = logging.getLogger(__name__)


class AlgorithmType(Enum):
    """算法类型枚举"""
    GREEDY = "greedy"
    GENETIC = "genetic"
    PARALLEL_GENETIC = "parallel_genetic"
    HYBRID = "hybrid"
    OPTIMIZER = "optimizer"


class SchedulingEngine:
    """统一的排课引擎"""
    
    def __init__(self, constraint_manager: Optional[ConstraintManager] = None,
                 default_algorithm: AlgorithmType = AlgorithmType.HYBRID,
                 enable_conflict_resolution: bool = True,
                 enable_optimization: bool = True):
        """
        初始化排课引擎
        
        Args:
            constraint_manager: 约束管理器
            default_algorithm: 默认算法
            enable_conflict_resolution: 是否启用冲突解决
            enable_optimization: 是否启用后优化
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        self.default_algorithm = default_algorithm
        self.enable_conflict_resolution = enable_conflict_resolution
        self.enable_optimization = enable_optimization
        
        # 算法实例
        self.algorithms = {
            AlgorithmType.GREEDY: GreedyScheduler(self.constraint_manager),
            AlgorithmType.GENETIC: GeneticAlgorithm(constraint_manager=self.constraint_manager),
            AlgorithmType.PARALLEL_GENETIC: ParallelGeneticAlgorithm(),
            AlgorithmType.HYBRID: HybridOptimizer(self.constraint_manager),
            AlgorithmType.OPTIMIZER: ScheduleOptimizer(self.constraint_manager),
        }
        
        # 冲突处理组件
        self.conflict_detector = ConflictDetector()
        self.conflict_resolver = ConflictResolver(self.constraint_manager)
        self.conflict_analyzer = ConflictAnalyzer()
        
        # 引擎状态
        self.is_initialized = False
        self.data_cache = {}
        
        # 统计信息
        self.stats = {
            'total_schedules_generated': 0,
            'successful_schedules': 0,
            'failed_schedules': 0,
            'average_generation_time': 0.0,
            'algorithm_usage': {alg.value: 0 for alg in AlgorithmType},
            'conflict_resolution_success_rate': 0.0,
        }
    
    def initialize(self, courses: List[Dict], teachers: List[Dict], 
                  classrooms: List[Dict], teacher_preferences: List[TeacherPreference] = None):
        """初始化引擎数据"""
        logger.info("Initializing scheduling engine")
        
        # 缓存数据
        self.data_cache = {
            'courses': courses,
            'teachers': teachers,
            'classrooms': classrooms,
            'teacher_preferences': teacher_preferences or [],
        }
        
        # 为所有算法设置数据
        self.constraint_manager.set_data_cache(courses, teachers, classrooms, teacher_preferences)
        
        # 初始化各个算法
        for algorithm_type, algorithm in self.algorithms.items():
            try:
                if hasattr(algorithm, 'set_data'):
                    algorithm.set_data(courses, teachers, classrooms, teacher_preferences)
                logger.debug(f"Initialized {algorithm_type.value} algorithm")
            except Exception as e:
                logger.error(f"Failed to initialize {algorithm_type.value}: {e}")
        
        self.is_initialized = True
        logger.info(f"Engine initialized with {len(courses)} courses, "
                   f"{len(teachers)} teachers, {len(classrooms)} classrooms")
    
    def generate_schedule(self, algorithm: Optional[AlgorithmType] = None,
                         algorithm_params: Dict[str, Any] = None,
                         validate_result: bool = True) -> ScheduleResult:
        """生成排课方案"""
        if not self.is_initialized:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
        algorithm = algorithm or self.default_algorithm
        algorithm_params = algorithm_params or {}
        
        start_time = time.time()
        self.stats['total_schedules_generated'] += 1
        self.stats['algorithm_usage'][algorithm.value] += 1
        
        logger.info(f"Generating schedule using {algorithm.value} algorithm")
        
        try:
            # 运行选定的算法
            result = self._run_algorithm(algorithm, algorithm_params)
            
            # 验证结果
            if validate_result:
                result = self._validate_and_enhance_result(result)
            
            # 冲突解决
            if self.enable_conflict_resolution and result.conflicts:
                result = self._resolve_conflicts(result)
            
            # 后优化
            if self.enable_optimization and result.is_valid:
                result = self._post_optimize(result)
            
            # 更新统计信息
            generation_time = time.time() - start_time
            result.generation_time = generation_time
            
            if result.is_valid:
                self.stats['successful_schedules'] += 1
            else:
                self.stats['failed_schedules'] += 1
            
            # 更新平均生成时间
            total_time = (self.stats['average_generation_time'] * 
                         (self.stats['total_schedules_generated'] - 1) + generation_time)
            self.stats['average_generation_time'] = total_time / self.stats['total_schedules_generated']
            
            logger.info(f"Schedule generation completed: "
                       f"fitness = {result.fitness_score:.2f}, "
                       f"conflicts = {len(result.conflicts)}, "
                       f"time = {generation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Schedule generation failed: {e}")
            self.stats['failed_schedules'] += 1
            
            # 返回空结果
            return ScheduleResult(
                assignments=[],
                conflicts=[],
                fitness_score=0.0,
                algorithm_used=f"{algorithm.value}_failed",
                generation_time=time.time() - start_time,
                metadata={'error': str(e)},
            )
    
    def _run_algorithm(self, algorithm: AlgorithmType, params: Dict[str, Any]) -> ScheduleResult:
        """运行指定算法"""
        algorithm_instance = self.algorithms[algorithm]
        
        # 更新算法参数
        if params and hasattr(algorithm_instance, 'update_parameters'):
            algorithm_instance.update_parameters(**params)
        
        # 运行算法
        if algorithm == AlgorithmType.GREEDY:
            return algorithm_instance.schedule()
        
        elif algorithm == AlgorithmType.GENETIC:
            best_individual = algorithm_instance.evolve()
            return ScheduleResult(
                assignments=best_individual.assignments,
                conflicts=best_individual.get_conflicts(),
                fitness_score=best_individual.fitness,
                algorithm_used='genetic',
                metadata=algorithm_instance.get_statistics(),
            )
        
        elif algorithm == AlgorithmType.PARALLEL_GENETIC:
            return algorithm_instance.evolve(
                self.data_cache['courses'],
                self.data_cache['teachers'],
                self.data_cache['classrooms'],
                self.data_cache['teacher_preferences']
            )
        
        elif algorithm == AlgorithmType.HYBRID:
            return algorithm_instance.optimize(
                self.data_cache['courses'],
                self.data_cache['teachers'],
                self.data_cache['classrooms'],
                self.data_cache['teacher_preferences']
            )
        
        elif algorithm == AlgorithmType.OPTIMIZER:
            # 需要初始解，先运行贪心算法
            greedy_result = self.algorithms[AlgorithmType.GREEDY].schedule()
            return algorithm_instance.optimize_schedule(
                greedy_result.assignments,
                self.data_cache['teachers'],
                self.data_cache['classrooms'],
                self.data_cache['courses']
            )
        
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _validate_and_enhance_result(self, result: ScheduleResult) -> ScheduleResult:
        """验证和增强结果"""
        # 检测冲突
        conflicts = self.conflict_detector.detect_all_conflicts(
            result.assignments,
            self.data_cache['courses'],
            self.data_cache['teachers'],
            self.data_cache['classrooms']
        )
        
        # 更新冲突信息
        result.conflicts = conflicts
        
        # 重新计算适应度
        if result.assignments:
            evaluation = self.constraint_manager.evaluate_schedule(result.assignments)
            result.fitness_score = evaluation['overall_fitness']
        
        return result
    
    def _resolve_conflicts(self, result: ScheduleResult) -> ScheduleResult:
        """解决冲突"""
        if not result.conflicts:
            return result
        
        logger.info(f"Resolving {len(result.conflicts)} conflicts")
        
        resolved_assignments, unresolved_conflicts = self.conflict_resolver.resolve_conflicts(
            result.assignments,
            result.conflicts,
            self.data_cache['teachers'],
            self.data_cache['classrooms']
        )
        
        # 更新结果
        result.assignments = resolved_assignments
        result.conflicts = unresolved_conflicts
        
        # 重新计算适应度
        if result.assignments:
            evaluation = self.constraint_manager.evaluate_schedule(result.assignments)
            result.fitness_score = evaluation['overall_fitness']
        
        # 更新冲突解决成功率
        total_conflicts = len(result.conflicts) + len(unresolved_conflicts)
        if total_conflicts > 0:
            success_rate = (total_conflicts - len(unresolved_conflicts)) / total_conflicts
            self.stats['conflict_resolution_success_rate'] = success_rate
        
        logger.info(f"Conflict resolution completed: {len(unresolved_conflicts)} unresolved")
        
        return result
    
    def _post_optimize(self, result: ScheduleResult) -> ScheduleResult:
        """后优化"""
        if not result.assignments:
            return result
        
        logger.info("Performing post-optimization")
        
        optimizer = self.algorithms[AlgorithmType.OPTIMIZER]
        optimized_result = optimizer.optimize_schedule(
            result.assignments,
            self.data_cache['teachers'],
            self.data_cache['classrooms'],
            self.data_cache['courses']
        )
        
        # 如果优化后更好，则使用优化结果
        if optimized_result.fitness_score > result.fitness_score:
            result = optimized_result
            result.metadata['post_optimized'] = True
            logger.info(f"Post-optimization improved fitness to {result.fitness_score:.2f}")
        else:
            logger.info("Post-optimization did not improve the result")
        
        return result
    
    def analyze_schedule(self, result: ScheduleResult) -> Dict[str, Any]:
        """分析排课结果"""
        if not result.assignments:
            return {'error': 'No assignments to analyze'}
        
        # 冲突分析
        conflict_analysis = self.conflict_analyzer.analyze_conflicts(
            result.conflicts,
            result.assignments,
            self.data_cache['courses'],
            self.data_cache['teachers'],
            self.data_cache['classrooms']
        )
        
        # 约束分析
        constraint_evaluation = self.constraint_manager.evaluate_schedule(result.assignments)
        
        # 资源利用率分析
        resource_analysis = self._analyze_resource_utilization(result.assignments)
        
        return {
            'schedule_summary': {
                'total_assignments': len(result.assignments),
                'fitness_score': result.fitness_score,
                'is_valid': result.is_valid,
                'conflicts': len(result.conflicts),
                'algorithm_used': result.algorithm_used,
                'generation_time': result.generation_time,
            },
            'conflict_analysis': conflict_analysis,
            'constraint_evaluation': constraint_evaluation,
            'resource_analysis': resource_analysis,
        }
    
    def _analyze_resource_utilization(self, assignments: List[Assignment]) -> Dict[str, Any]:
        """分析资源利用率"""
        # 教师利用率
        teacher_usage = {}
        for assignment in assignments:
            teacher_id = assignment.teacher_id
            teacher_usage[teacher_id] = teacher_usage.get(teacher_id, 0) + 1
        
        # 教室利用率
        classroom_usage = {}
        for assignment in assignments:
            classroom_id = assignment.classroom_id
            classroom_usage[classroom_id] = classroom_usage.get(classroom_id, 0) + 1
        
        # 时间段利用率
        time_usage = {}
        for assignment in assignments:
            time_key = (assignment.day_of_week, assignment.time_slot)
            time_usage[time_key] = time_usage.get(time_key, 0) + 1
        
        return {
            'teacher_utilization': {
                'usage_distribution': teacher_usage,
                'average_load': sum(teacher_usage.values()) / len(teacher_usage) if teacher_usage else 0,
                'max_load': max(teacher_usage.values()) if teacher_usage else 0,
                'min_load': min(teacher_usage.values()) if teacher_usage else 0,
            },
            'classroom_utilization': {
                'usage_distribution': classroom_usage,
                'average_usage': sum(classroom_usage.values()) / len(classroom_usage) if classroom_usage else 0,
                'max_usage': max(classroom_usage.values()) if classroom_usage else 0,
                'min_usage': min(classroom_usage.values()) if classroom_usage else 0,
            },
            'time_utilization': {
                'usage_distribution': time_usage,
                'peak_times': sorted(time_usage.items(), key=lambda x: x[1], reverse=True)[:5],
                'total_time_slots_used': len(time_usage),
            },
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        return {
            'engine_stats': self.stats.copy(),
            'constraint_manager_stats': self.constraint_manager.get_statistics(),
            'conflict_detector_stats': self.conflict_detector.get_statistics(),
            'conflict_resolver_stats': self.conflict_resolver.get_statistics(),
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'total_schedules_generated': 0,
            'successful_schedules': 0,
            'failed_schedules': 0,
            'average_generation_time': 0.0,
            'algorithm_usage': {alg.value: 0 for alg in AlgorithmType},
            'conflict_resolution_success_rate': 0.0,
        }
        
        # 重置各组件统计
        self.constraint_manager.reset_statistics()
        self.conflict_detector.reset_statistics()
        self.conflict_resolver.reset_statistics()
    
    def export_schedule(self, result: ScheduleResult, format: str = 'json') -> Union[str, Dict]:
        """导出排课结果"""
        if format == 'json':
            return result.to_json()
        elif format == 'dict':
            return result.to_dict()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_schedule(self, data: Union[str, Dict]) -> ScheduleResult:
        """导入排课结果"""
        if isinstance(data, str):
            import json
            data = json.loads(data)
        
        assignments = [Assignment.from_dict(a) for a in data['assignments']]
        conflicts = []  # 需要重新检测冲突
        
        result = ScheduleResult(
            assignments=assignments,
            conflicts=conflicts,
            fitness_score=data.get('fitness_score', 0.0),
            algorithm_used=data.get('algorithm_used', 'imported'),
            generation_time=data.get('generation_time', 0.0),
            metadata=data.get('metadata', {}),
        )
        
        # 重新验证和检测冲突
        if self.is_initialized:
            result = self._validate_and_enhance_result(result)
        
        return result
