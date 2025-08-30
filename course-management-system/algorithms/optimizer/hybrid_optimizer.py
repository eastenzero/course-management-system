# file: algorithms/optimizer/hybrid_optimizer.py
# 功能: 混合优化器 - 结合多种算法的优化策略

import time
import logging
from typing import List, Dict, Any, Optional
from ..models import Assignment, ScheduleResult
from ..constraints.manager import ConstraintManager
from ..genetic.genetic_algorithm import GeneticAlgorithm
from ..heuristic.greedy_scheduler import GreedyScheduler
from .schedule_optimizer import ScheduleOptimizer
from .parallel_ga import ParallelGeneticAlgorithm

logger = logging.getLogger(__name__)


class HybridOptimizer:
    """混合优化器 - 结合多种算法的优化策略"""
    
    def __init__(self, constraint_manager: Optional[ConstraintManager] = None,
                 optimization_sequence: List[str] = None,
                 time_limits: Dict[str, float] = None,
                 quality_thresholds: Dict[str, float] = None):
        """
        初始化混合优化器
        
        Args:
            constraint_manager: 约束管理器
            optimization_sequence: 优化算法序列
            time_limits: 各算法的时间限制
            quality_thresholds: 质量阈值，达到后可提前停止
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        
        if optimization_sequence is None:
            self.optimization_sequence = [
                'greedy',           # 快速生成初始解
                'genetic',          # 遗传算法优化
                'local_search',     # 局部搜索精细调优
            ]
        else:
            self.optimization_sequence = optimization_sequence
        
        # 默认时间限制（秒）
        if time_limits is None:
            self.time_limits = {
                'greedy': 30,
                'genetic': 300,
                'parallel_genetic': 600,
                'local_search': 120,
                'optimizer': 180,
            }
        else:
            self.time_limits = time_limits
        
        # 默认质量阈值
        if quality_thresholds is None:
            self.quality_thresholds = {
                'greedy': 60.0,
                'genetic': 85.0,
                'parallel_genetic': 90.0,
                'local_search': 95.0,
                'optimizer': 98.0,
            }
        else:
            self.quality_thresholds = quality_thresholds
        
        # 算法实例
        self.greedy_scheduler = GreedyScheduler(self.constraint_manager)
        self.genetic_algorithm = GeneticAlgorithm(constraint_manager=self.constraint_manager)
        self.parallel_genetic = ParallelGeneticAlgorithm()
        self.schedule_optimizer = ScheduleOptimizer(self.constraint_manager)
        
        # 统计信息
        self.stats = {
            'total_time': 0.0,
            'algorithm_times': {},
            'algorithm_results': {},
            'best_fitness_progression': [],
            'early_stops': [],
        }
    
    def optimize(self, courses: List[Dict], teachers: List[Dict],
                classrooms: List[Dict], teacher_preferences: List[Any] = None) -> ScheduleResult:
        """执行混合优化"""
        start_time = time.time()
        
        logger.info(f"Starting hybrid optimization with sequence: {self.optimization_sequence}")
        
        # 设置数据
        self._set_data_for_all_algorithms(courses, teachers, classrooms, teacher_preferences)
        
        current_result = None
        best_result = None
        best_fitness = float('-inf')
        
        for algorithm in self.optimization_sequence:
            algorithm_start_time = time.time()
            
            logger.info(f"Running algorithm: {algorithm}")
            
            try:
                # 运行算法
                if algorithm == 'greedy':
                    result = self._run_greedy(courses, teachers, classrooms)
                elif algorithm == 'genetic':
                    result = self._run_genetic(courses, teachers, classrooms, current_result)
                elif algorithm == 'parallel_genetic':
                    result = self._run_parallel_genetic(courses, teachers, classrooms, current_result)
                elif algorithm == 'local_search':
                    result = self._run_local_search(courses, teachers, classrooms, current_result)
                elif algorithm == 'optimizer':
                    result = self._run_optimizer(courses, teachers, classrooms, current_result)
                else:
                    logger.warning(f"Unknown algorithm: {algorithm}")
                    continue
                
                algorithm_time = time.time() - algorithm_start_time
                self.stats['algorithm_times'][algorithm] = algorithm_time
                self.stats['algorithm_results'][algorithm] = {
                    'fitness': result.fitness_score,
                    'conflicts': len(result.conflicts),
                    'time': algorithm_time,
                }
                
                # 更新最佳结果
                if result.fitness_score > best_fitness:
                    best_fitness = result.fitness_score
                    best_result = result
                    current_result = result
                
                self.stats['best_fitness_progression'].append({
                    'algorithm': algorithm,
                    'fitness': best_fitness,
                    'time': time.time() - start_time,
                })
                
                logger.info(f"{algorithm} completed: fitness = {result.fitness_score:.2f}, "
                           f"time = {algorithm_time:.2f}s")
                
                # 检查质量阈值
                threshold = self.quality_thresholds.get(algorithm, 100.0)
                if result.fitness_score >= threshold:
                    self.stats['early_stops'].append({
                        'algorithm': algorithm,
                        'fitness': result.fitness_score,
                        'threshold': threshold,
                    })
                    logger.info(f"Quality threshold reached for {algorithm}, continuing to next algorithm")
                
                # 检查时间限制
                if algorithm_time >= self.time_limits.get(algorithm, float('inf')):
                    logger.info(f"Time limit reached for {algorithm}")
                
            except Exception as e:
                logger.error(f"Algorithm {algorithm} failed: {e}")
                continue
        
        self.stats['total_time'] = time.time() - start_time
        
        # 更新最终结果的元数据
        if best_result:
            best_result.algorithm_used = 'hybrid'
            best_result.generation_time = self.stats['total_time']
            best_result.metadata.update({
                'optimization_sequence': self.optimization_sequence,
                'hybrid_stats': self.stats.copy(),
            })
        
        logger.info(f"Hybrid optimization completed: "
                   f"best fitness = {best_fitness:.2f}, "
                   f"total time = {self.stats['total_time']:.2f}s")
        
        return best_result or ScheduleResult(
            assignments=[],
            conflicts=[],
            fitness_score=0.0,
            algorithm_used='hybrid_failed',
            generation_time=self.stats['total_time'],
        )
    
    def _set_data_for_all_algorithms(self, courses: List[Dict], teachers: List[Dict],
                                   classrooms: List[Dict], teacher_preferences: List[Any] = None):
        """为所有算法设置数据"""
        self.greedy_scheduler.set_data(courses, teachers, classrooms, teacher_preferences)
        self.genetic_algorithm.set_data(courses, teachers, classrooms, teacher_preferences)
        self.constraint_manager.set_data_cache(courses, teachers, classrooms, teacher_preferences)
    
    def _run_greedy(self, courses: List[Dict], teachers: List[Dict],
                   classrooms: List[Dict]) -> ScheduleResult:
        """运行贪心算法"""
        return self.greedy_scheduler.schedule()
    
    def _run_genetic(self, courses: List[Dict], teachers: List[Dict],
                    classrooms: List[Dict], seed_result: Optional[ScheduleResult] = None) -> ScheduleResult:
        """运行遗传算法"""
        if seed_result and seed_result.assignments:
            # 使用种子解
            from ..genetic.individual import Individual
            seed_individual = Individual(assignments=seed_result.assignments)
            best_individual = self.genetic_algorithm.evolve_with_seed(seed_individual)
        else:
            best_individual = self.genetic_algorithm.evolve()
        
        return ScheduleResult(
            assignments=best_individual.assignments,
            conflicts=best_individual.get_conflicts(),
            fitness_score=best_individual.fitness,
            algorithm_used='genetic',
            generation_time=self.genetic_algorithm.get_statistics()['total_time'],
            metadata=self.genetic_algorithm.get_statistics(),
        )
    
    def _run_parallel_genetic(self, courses: List[Dict], teachers: List[Dict],
                            classrooms: List[Dict], seed_result: Optional[ScheduleResult] = None) -> ScheduleResult:
        """运行并行遗传算法"""
        return self.parallel_genetic.evolve(courses, teachers, classrooms)
    
    def _run_local_search(self, courses: List[Dict], teachers: List[Dict],
                         classrooms: List[Dict], initial_result: Optional[ScheduleResult] = None) -> ScheduleResult:
        """运行局部搜索"""
        if not initial_result or not initial_result.assignments:
            # 如果没有初始解，先运行贪心算法
            initial_result = self._run_greedy(courses, teachers, classrooms)
        
        from ..heuristic.local_search import LocalSearch
        local_search = LocalSearch(self.constraint_manager)
        return local_search.improve_schedule(initial_result.assignments, teachers, classrooms)
    
    def _run_optimizer(self, courses: List[Dict], teachers: List[Dict],
                      classrooms: List[Dict], initial_result: Optional[ScheduleResult] = None) -> ScheduleResult:
        """运行优化器"""
        if not initial_result or not initial_result.assignments:
            # 如果没有初始解，先运行贪心算法
            initial_result = self._run_greedy(courses, teachers, classrooms)
        
        return self.schedule_optimizer.optimize_schedule(
            initial_result.assignments, teachers, classrooms, courses
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def get_algorithm_comparison(self) -> Dict[str, Any]:
        """获取算法比较结果"""
        comparison = {
            'algorithms_used': list(self.stats['algorithm_results'].keys()),
            'best_algorithm': None,
            'worst_algorithm': None,
            'fitness_improvement': {},
            'time_efficiency': {},
        }
        
        if self.stats['algorithm_results']:
            # 找到最佳和最差算法
            best_fitness = max(r['fitness'] for r in self.stats['algorithm_results'].values())
            worst_fitness = min(r['fitness'] for r in self.stats['algorithm_results'].values())
            
            for alg, result in self.stats['algorithm_results'].items():
                if result['fitness'] == best_fitness:
                    comparison['best_algorithm'] = alg
                if result['fitness'] == worst_fitness:
                    comparison['worst_algorithm'] = alg
                
                # 计算时间效率（适应度/时间）
                comparison['time_efficiency'][alg] = result['fitness'] / result['time'] if result['time'] > 0 else 0
            
            # 计算适应度改进
            prev_fitness = 0
            for progress in self.stats['best_fitness_progression']:
                improvement = progress['fitness'] - prev_fitness
                comparison['fitness_improvement'][progress['algorithm']] = improvement
                prev_fitness = progress['fitness']
        
        return comparison
    
    def export_optimization_report(self) -> str:
        """导出优化报告"""
        report = []
        report.append("# 混合优化报告\n")
        
        # 总体统计
        report.append("## 总体统计")
        report.append(f"- 总优化时间: {self.stats['total_time']:.2f} 秒")
        report.append(f"- 使用算法数量: {len(self.stats['algorithm_results'])}")
        
        # 算法结果
        if self.stats['algorithm_results']:
            report.append("\n## 算法结果")
            for alg, result in self.stats['algorithm_results'].items():
                report.append(f"\n### {alg}")
                report.append(f"- 适应度: {result['fitness']:.2f}")
                report.append(f"- 冲突数: {result['conflicts']}")
                report.append(f"- 运行时间: {result['time']:.2f} 秒")
        
        # 适应度进展
        if self.stats['best_fitness_progression']:
            report.append("\n## 适应度进展")
            for progress in self.stats['best_fitness_progression']:
                report.append(f"- {progress['algorithm']}: {progress['fitness']:.2f} "
                            f"(时间: {progress['time']:.2f}s)")
        
        # 早停情况
        if self.stats['early_stops']:
            report.append("\n## 早停情况")
            for stop in self.stats['early_stops']:
                report.append(f"- {stop['algorithm']}: 达到阈值 {stop['threshold']:.2f} "
                            f"(实际: {stop['fitness']:.2f})")
        
        # 算法比较
        comparison = self.get_algorithm_comparison()
        if comparison['best_algorithm']:
            report.append(f"\n## 算法比较")
            report.append(f"- 最佳算法: {comparison['best_algorithm']}")
            report.append(f"- 最差算法: {comparison['worst_algorithm']}")
            
            report.append("\n### 时间效率排名")
            sorted_efficiency = sorted(comparison['time_efficiency'].items(), 
                                     key=lambda x: x[1], reverse=True)
            for i, (alg, efficiency) in enumerate(sorted_efficiency, 1):
                report.append(f"{i}. {alg}: {efficiency:.2f} 适应度/秒")
        
        return "\n".join(report)
