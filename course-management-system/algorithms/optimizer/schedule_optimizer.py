# file: algorithms/optimizer/schedule_optimizer.py
# 功能: 排课优化器 - 局部搜索和优化算法

import random
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from ..models import Assignment, ScheduleResult
from ..constraints.manager import ConstraintManager
from ..heuristic.local_search import LocalSearch

logger = logging.getLogger(__name__)


class ScheduleOptimizer:
    """排课优化器 - 使用多种优化策略改进排课方案"""
    
    def __init__(self, constraint_manager: Optional[ConstraintManager] = None,
                 optimization_strategies: List[str] = None,
                 max_iterations: int = 1000,
                 improvement_threshold: float = 0.01,
                 no_improvement_limit: int = 100):
        """
        初始化排课优化器
        
        Args:
            constraint_manager: 约束管理器
            optimization_strategies: 优化策略列表
            max_iterations: 最大迭代次数
            improvement_threshold: 改进阈值
            no_improvement_limit: 无改进限制次数
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        
        if optimization_strategies is None:
            self.optimization_strategies = [
                'local_search',
                'simulated_annealing',
                'tabu_search',
                'variable_neighborhood_search',
                'greedy_improvement',
            ]
        else:
            self.optimization_strategies = optimization_strategies
        
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        self.no_improvement_limit = no_improvement_limit
        
        # 局部搜索器
        self.local_search = LocalSearch(constraint_manager)
        
        # 统计信息
        self.stats = {
            'total_iterations': 0,
            'improvements': 0,
            'best_fitness': float('-inf'),
            'initial_fitness': 0.0,
            'final_fitness': 0.0,
            'optimization_time': 0.0,
            'strategy_usage': {strategy: 0 for strategy in self.optimization_strategies},
            'strategy_success': {strategy: 0 for strategy in self.optimization_strategies},
        }
    
    def optimize_schedule(self, initial_assignments: List[Assignment],
                         teachers: List[Dict], classrooms: List[Dict],
                         courses: List[Dict] = None) -> ScheduleResult:
        """优化排课方案"""
        start_time = time.time()
        
        current_assignments = [a.copy() for a in initial_assignments]
        
        # 计算初始适应度
        initial_evaluation = self.constraint_manager.evaluate_schedule(current_assignments)
        current_fitness = initial_evaluation['overall_fitness']
        best_fitness = current_fitness
        best_assignments = [a.copy() for a in current_assignments]
        
        self.stats['initial_fitness'] = current_fitness
        self.stats['best_fitness'] = best_fitness
        
        no_improvement_count = 0
        
        logger.info(f"Starting schedule optimization with initial fitness: {current_fitness:.2f}")
        
        for iteration in range(self.max_iterations):
            self.stats['total_iterations'] = iteration + 1
            
            # 选择优化策略
            strategy = self._select_optimization_strategy(iteration)
            self.stats['strategy_usage'][strategy] += 1
            
            # 应用优化策略
            improved_assignments, improved_fitness = self._apply_optimization_strategy(
                strategy, current_assignments, teachers, classrooms, courses
            )
            
            # 检查是否有改进
            improvement = improved_fitness - current_fitness
            if improvement > self.improvement_threshold:
                current_assignments = improved_assignments
                current_fitness = improved_fitness
                no_improvement_count = 0
                self.stats['improvements'] += 1
                self.stats['strategy_success'][strategy] += 1
                
                # 更新最佳解
                if improved_fitness > best_fitness:
                    best_fitness = improved_fitness
                    best_assignments = [a.copy() for a in improved_assignments]
                    self.stats['best_fitness'] = best_fitness
                
                logger.debug(f"Iteration {iteration}: {strategy} improved fitness by {improvement:.4f}")
            else:
                no_improvement_count += 1
            
            # 检查停止条件
            if no_improvement_count >= self.no_improvement_limit:
                logger.info(f"Optimization converged at iteration {iteration}")
                break
            
            # 定期输出进度
            if iteration % 100 == 0:
                logger.info(f"Iteration {iteration}: Best fitness = {best_fitness:.4f}")
        
        self.stats['final_fitness'] = best_fitness
        self.stats['optimization_time'] = time.time() - start_time
        
        # 检测最终冲突
        conflicts = self.constraint_manager.find_conflicts(best_assignments)
        
        result = ScheduleResult(
            assignments=best_assignments,
            conflicts=conflicts,
            fitness_score=best_fitness,
            algorithm_used='optimizer',
            generation_time=self.stats['optimization_time'],
            metadata={
                'initial_fitness': self.stats['initial_fitness'],
                'improvement': best_fitness - self.stats['initial_fitness'],
                'stats': self.stats.copy(),
                'strategies_used': self.optimization_strategies,
            }
        )
        
        logger.info(f"Optimization completed: fitness improved from "
                   f"{self.stats['initial_fitness']:.4f} to {best_fitness:.4f}")
        
        return result
    
    def _select_optimization_strategy(self, iteration: int) -> str:
        """选择优化策略"""
        # 自适应策略选择
        if iteration < 100:
            # 早期使用局部搜索
            return 'local_search'
        elif iteration < 300:
            # 中期使用模拟退火
            return 'simulated_annealing'
        elif iteration < 600:
            # 后期使用禁忌搜索
            return 'tabu_search'
        else:
            # 最后阶段随机选择
            return random.choice(self.optimization_strategies)
    
    def _apply_optimization_strategy(self, strategy: str, assignments: List[Assignment],
                                   teachers: List[Dict], classrooms: List[Dict],
                                   courses: List[Dict] = None) -> Tuple[List[Assignment], float]:
        """应用优化策略"""
        if strategy == 'local_search':
            return self._local_search_optimization(assignments, teachers, classrooms)
        elif strategy == 'simulated_annealing':
            return self._simulated_annealing_optimization(assignments, teachers, classrooms)
        elif strategy == 'tabu_search':
            return self._tabu_search_optimization(assignments, teachers, classrooms)
        elif strategy == 'variable_neighborhood_search':
            return self._variable_neighborhood_search(assignments, teachers, classrooms)
        elif strategy == 'greedy_improvement':
            return self._greedy_improvement(assignments, teachers, classrooms)
        else:
            # 默认使用局部搜索
            return self._local_search_optimization(assignments, teachers, classrooms)
    
    def _local_search_optimization(self, assignments: List[Assignment],
                                 teachers: List[Dict], classrooms: List[Dict]) -> Tuple[List[Assignment], float]:
        """局部搜索优化"""
        current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 尝试多种邻域操作
        best_assignments = assignments
        best_fitness = current_fitness
        
        # 时间交换操作
        for i in range(min(10, len(assignments))):  # 限制尝试次数
            for j in range(i + 1, min(i + 10, len(assignments))):
                neighbor = self._swap_times(assignments, i, j)
                fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_assignments = neighbor
        
        return best_assignments, best_fitness
    
    def _simulated_annealing_optimization(self, assignments: List[Assignment],
                                        teachers: List[Dict], classrooms: List[Dict]) -> Tuple[List[Assignment], float]:
        """模拟退火优化"""
        current_assignments = assignments
        current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 模拟退火参数
        initial_temperature = 100.0
        cooling_rate = 0.95
        temperature = initial_temperature
        
        for _ in range(10):  # 限制内部迭代次数
            # 生成邻域解
            neighbor = self._generate_random_neighbor(current_assignments, teachers, classrooms)
            neighbor_fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
            
            # 接受准则
            delta = neighbor_fitness - current_fitness
            if delta > 0 or random.random() < np.exp(delta / temperature):
                current_assignments = neighbor
                current_fitness = neighbor_fitness
            
            temperature *= cooling_rate
        
        return current_assignments, current_fitness
    
    def _tabu_search_optimization(self, assignments: List[Assignment],
                                teachers: List[Dict], classrooms: List[Dict]) -> Tuple[List[Assignment], float]:
        """禁忌搜索优化"""
        current_assignments = assignments
        current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 禁忌列表（简化版本）
        tabu_list = set()
        tabu_tenure = 5
        
        best_assignments = current_assignments
        best_fitness = current_fitness
        
        for _ in range(10):  # 限制迭代次数
            # 生成候选解
            candidates = []
            for _ in range(5):  # 生成5个候选解
                neighbor = self._generate_random_neighbor(current_assignments, teachers, classrooms)
                neighbor_hash = self._hash_assignments(neighbor)
                
                if neighbor_hash not in tabu_list:
                    fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                    candidates.append((neighbor, fitness, neighbor_hash))
            
            if candidates:
                # 选择最佳候选解
                best_candidate = max(candidates, key=lambda x: x[1])
                current_assignments, current_fitness, assignment_hash = best_candidate
                
                # 更新禁忌列表
                tabu_list.add(assignment_hash)
                if len(tabu_list) > tabu_tenure:
                    tabu_list.pop()
                
                # 更新全局最佳解
                if current_fitness > best_fitness:
                    best_fitness = current_fitness
                    best_assignments = current_assignments
        
        return best_assignments, best_fitness
    
    def _variable_neighborhood_search(self, assignments: List[Assignment],
                                    teachers: List[Dict], classrooms: List[Dict]) -> Tuple[List[Assignment], float]:
        """变邻域搜索"""
        current_assignments = assignments
        current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 定义不同的邻域操作
        neighborhoods = ['swap_times', 'move_time', 'change_classroom']
        
        for neighborhood in neighborhoods:
            # 在当前邻域中搜索
            if neighborhood == 'swap_times':
                neighbor = self._generate_swap_neighbor(current_assignments)
            elif neighborhood == 'move_time':
                neighbor = self._generate_move_neighbor(current_assignments)
            else:  # change_classroom
                neighbor = self._generate_classroom_neighbor(current_assignments, classrooms)
            
            if neighbor:
                fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                if fitness > current_fitness:
                    current_assignments = neighbor
                    current_fitness = fitness
                    break  # 找到改进解，重新开始
        
        return current_assignments, current_fitness
    
    def _greedy_improvement(self, assignments: List[Assignment],
                          teachers: List[Dict], classrooms: List[Dict]) -> Tuple[List[Assignment], float]:
        """贪心改进"""
        current_assignments = [a.copy() for a in assignments]
        current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 随机选择一个分配进行改进
        if current_assignments:
            index = random.randint(0, len(current_assignments) - 1)
            assignment = current_assignments[index]
            
            # 尝试更好的时间段
            best_assignment = assignment.copy()
            best_fitness = current_fitness
            
            for day in range(1, 6):
                for time_slot in range(1, 11):
                    if day != assignment.day_of_week or time_slot != assignment.time_slot:
                        test_assignment = assignment.copy()
                        test_assignment.day_of_week = day
                        test_assignment.time_slot = time_slot
                        
                        test_assignments = current_assignments.copy()
                        test_assignments[index] = test_assignment
                        
                        if self.constraint_manager.check_hard_constraints(
                            test_assignment, 
                            test_assignments[:index] + test_assignments[index+1:]
                        ):
                            fitness = self.constraint_manager.evaluate_schedule(test_assignments)['overall_fitness']
                            if fitness > best_fitness:
                                best_fitness = fitness
                                best_assignment = test_assignment
            
            current_assignments[index] = best_assignment
            current_fitness = best_fitness
        
        return current_assignments, current_fitness
    
    def _swap_times(self, assignments: List[Assignment], i: int, j: int) -> List[Assignment]:
        """交换两个分配的时间"""
        neighbor = [a.copy() for a in assignments]
        neighbor[i].day_of_week, neighbor[j].day_of_week = neighbor[j].day_of_week, neighbor[i].day_of_week
        neighbor[i].time_slot, neighbor[j].time_slot = neighbor[j].time_slot, neighbor[i].time_slot
        return neighbor
    
    def _generate_random_neighbor(self, assignments: List[Assignment],
                                teachers: List[Dict], classrooms: List[Dict]) -> List[Assignment]:
        """生成随机邻域解"""
        neighbor = [a.copy() for a in assignments]
        
        if neighbor:
            # 随机选择操作类型
            operation = random.choice(['swap_times', 'move_time', 'change_classroom'])
            
            if operation == 'swap_times' and len(neighbor) >= 2:
                i, j = random.sample(range(len(neighbor)), 2)
                neighbor[i].day_of_week, neighbor[j].day_of_week = neighbor[j].day_of_week, neighbor[i].day_of_week
                neighbor[i].time_slot, neighbor[j].time_slot = neighbor[j].time_slot, neighbor[i].time_slot
            
            elif operation == 'move_time':
                i = random.randint(0, len(neighbor) - 1)
                neighbor[i].day_of_week = random.randint(1, 5)
                neighbor[i].time_slot = random.randint(1, 10)
            
            elif operation == 'change_classroom':
                i = random.randint(0, len(neighbor) - 1)
                classroom = random.choice(classrooms)
                neighbor[i].classroom_id = classroom['id']
        
        return neighbor
    
    def _generate_swap_neighbor(self, assignments: List[Assignment]) -> Optional[List[Assignment]]:
        """生成交换邻域解"""
        if len(assignments) < 2:
            return None
        
        neighbor = [a.copy() for a in assignments]
        i, j = random.sample(range(len(neighbor)), 2)
        neighbor[i].day_of_week, neighbor[j].day_of_week = neighbor[j].day_of_week, neighbor[i].day_of_week
        neighbor[i].time_slot, neighbor[j].time_slot = neighbor[j].time_slot, neighbor[i].time_slot
        return neighbor
    
    def _generate_move_neighbor(self, assignments: List[Assignment]) -> Optional[List[Assignment]]:
        """生成移动邻域解"""
        if not assignments:
            return None
        
        neighbor = [a.copy() for a in assignments]
        i = random.randint(0, len(neighbor) - 1)
        neighbor[i].day_of_week = random.randint(1, 5)
        neighbor[i].time_slot = random.randint(1, 10)
        return neighbor
    
    def _generate_classroom_neighbor(self, assignments: List[Assignment],
                                   classrooms: List[Dict]) -> Optional[List[Assignment]]:
        """生成教室变更邻域解"""
        if not assignments or not classrooms:
            return None
        
        neighbor = [a.copy() for a in assignments]
        i = random.randint(0, len(neighbor) - 1)
        classroom = random.choice(classrooms)
        neighbor[i].classroom_id = classroom['id']
        return neighbor
    
    def _hash_assignments(self, assignments: List[Assignment]) -> str:
        """计算分配的哈希值"""
        assignment_tuples = []
        for a in assignments:
            assignment_tuples.append((a.course_id, a.teacher_id, a.classroom_id, a.day_of_week, a.time_slot))
        return str(hash(tuple(sorted(assignment_tuples))))
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        strategy_success_rates = {}
        for strategy in self.optimization_strategies:
            usage = self.stats['strategy_usage'][strategy]
            success = self.stats['strategy_success'][strategy]
            strategy_success_rates[strategy] = success / usage if usage > 0 else 0.0
        
        return {
            'total_iterations': self.stats['total_iterations'],
            'improvements': self.stats['improvements'],
            'improvement_rate': (self.stats['improvements'] / self.stats['total_iterations'] 
                               if self.stats['total_iterations'] > 0 else 0.0),
            'initial_fitness': self.stats['initial_fitness'],
            'final_fitness': self.stats['final_fitness'],
            'total_improvement': self.stats['final_fitness'] - self.stats['initial_fitness'],
            'optimization_time': self.stats['optimization_time'],
            'strategy_usage': self.stats['strategy_usage'].copy(),
            'strategy_success': self.stats['strategy_success'].copy(),
            'strategy_success_rates': strategy_success_rates,
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'total_iterations': 0,
            'improvements': 0,
            'best_fitness': float('-inf'),
            'initial_fitness': 0.0,
            'final_fitness': 0.0,
            'optimization_time': 0.0,
            'strategy_usage': {strategy: 0 for strategy in self.optimization_strategies},
            'strategy_success': {strategy: 0 for strategy in self.optimization_strategies},
        }
