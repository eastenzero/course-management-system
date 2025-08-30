# file: algorithms/heuristic/local_search.py
# 功能: 局部搜索算法

import random
import logging
from typing import List, Dict, Any, Optional
from ..models import Assignment, ScheduleResult
from ..constraints.manager import ConstraintManager

logger = logging.getLogger(__name__)


class LocalSearch:
    """局部搜索算法"""
    
    def __init__(self, constraint_manager: Optional[ConstraintManager] = None,
                 max_iterations: int = 1000,
                 max_no_improvement: int = 100,
                 search_strategy: str = 'best_improvement'):
        """
        初始化局部搜索算法
        
        Args:
            constraint_manager: 约束管理器
            max_iterations: 最大迭代次数
            max_no_improvement: 最大无改进次数
            search_strategy: 搜索策略 ('best_improvement', 'first_improvement', 'random')
        """
        self.constraint_manager = constraint_manager or ConstraintManager()
        self.max_iterations = max_iterations
        self.max_no_improvement = max_no_improvement
        self.search_strategy = search_strategy
        
        # 统计信息
        self.stats = {
            'iterations': 0,
            'improvements': 0,
            'best_fitness': float('-inf'),
            'initial_fitness': 0.0,
            'final_fitness': 0.0,
        }
    
    def improve_schedule(self, initial_assignments: List[Assignment],
                        teachers: List[Dict], classrooms: List[Dict]) -> ScheduleResult:
        """改进现有排课方案"""
        current_assignments = [a.copy() for a in initial_assignments]
        
        # 计算初始适应度
        initial_evaluation = self.constraint_manager.evaluate_schedule(current_assignments)
        current_fitness = initial_evaluation['overall_fitness']
        best_fitness = current_fitness
        best_assignments = [a.copy() for a in current_assignments]
        
        self.stats['initial_fitness'] = current_fitness
        self.stats['best_fitness'] = best_fitness
        
        no_improvement_count = 0
        
        logger.info(f"Starting local search with initial fitness: {current_fitness:.2f}")
        
        for iteration in range(self.max_iterations):
            self.stats['iterations'] = iteration + 1
            
            # 生成邻域解
            if self.search_strategy == 'best_improvement':
                improved_assignments, improved_fitness = self._best_improvement_search(
                    current_assignments, teachers, classrooms
                )
            elif self.search_strategy == 'first_improvement':
                improved_assignments, improved_fitness = self._first_improvement_search(
                    current_assignments, teachers, classrooms
                )
            else:  # random
                improved_assignments, improved_fitness = self._random_search(
                    current_assignments, teachers, classrooms
                )
            
            # 检查是否有改进
            if improved_fitness > current_fitness:
                current_assignments = improved_assignments
                current_fitness = improved_fitness
                no_improvement_count = 0
                self.stats['improvements'] += 1
                
                # 更新最佳解
                if improved_fitness > best_fitness:
                    best_fitness = improved_fitness
                    best_assignments = [a.copy() for a in improved_assignments]
                    self.stats['best_fitness'] = best_fitness
                
                logger.debug(f"Iteration {iteration}: Improved fitness to {improved_fitness:.2f}")
            else:
                no_improvement_count += 1
            
            # 检查停止条件
            if no_improvement_count >= self.max_no_improvement:
                logger.info(f"Local search converged at iteration {iteration}")
                break
        
        self.stats['final_fitness'] = best_fitness
        
        # 检测冲突
        conflicts = self.constraint_manager.find_conflicts(best_assignments)
        
        result = ScheduleResult(
            assignments=best_assignments,
            conflicts=conflicts,
            fitness_score=best_fitness,
            algorithm_used='local_search',
            metadata={
                'initial_fitness': self.stats['initial_fitness'],
                'improvement': best_fitness - self.stats['initial_fitness'],
                'stats': self.stats.copy(),
            }
        )
        
        logger.info(f"Local search completed: fitness improved from "
                   f"{self.stats['initial_fitness']:.2f} to {best_fitness:.2f}")
        
        return result
    
    def _best_improvement_search(self, assignments: List[Assignment],
                               teachers: List[Dict], classrooms: List[Dict]) -> tuple:
        """最佳改进搜索"""
        best_assignments = assignments
        best_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 尝试所有可能的邻域操作
        for i, assignment in enumerate(assignments):
            # 时间交换操作
            for j in range(i + 1, len(assignments)):
                neighbor = self._swap_times(assignments, i, j)
                fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_assignments = neighbor
            
            # 时间移动操作
            for day in range(1, 6):
                for time_slot in range(1, 11):
                    if day != assignment.day_of_week or time_slot != assignment.time_slot:
                        neighbor = self._move_time(assignments, i, day, time_slot)
                        if neighbor:
                            fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                            
                            if fitness > best_fitness:
                                best_fitness = fitness
                                best_assignments = neighbor
            
            # 教室更换操作
            for classroom in classrooms:
                if classroom['id'] != assignment.classroom_id:
                    neighbor = self._change_classroom(assignments, i, classroom['id'])
                    if neighbor:
                        fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                        
                        if fitness > best_fitness:
                            best_fitness = fitness
                            best_assignments = neighbor
        
        return best_assignments, best_fitness
    
    def _first_improvement_search(self, assignments: List[Assignment],
                                teachers: List[Dict], classrooms: List[Dict]) -> tuple:
        """首次改进搜索"""
        current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
        
        # 随机尝试邻域操作
        operations = ['swap_times', 'move_time', 'change_classroom']
        random.shuffle(operations)
        
        for operation in operations:
            if operation == 'swap_times':
                # 随机选择两个分配进行时间交换
                if len(assignments) >= 2:
                    i, j = random.sample(range(len(assignments)), 2)
                    neighbor = self._swap_times(assignments, i, j)
                    fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                    
                    if fitness > current_fitness:
                        return neighbor, fitness
            
            elif operation == 'move_time':
                # 随机选择一个分配进行时间移动
                i = random.randint(0, len(assignments) - 1)
                day = random.randint(1, 5)
                time_slot = random.randint(1, 10)
                
                neighbor = self._move_time(assignments, i, day, time_slot)
                if neighbor:
                    fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                    
                    if fitness > current_fitness:
                        return neighbor, fitness
            
            elif operation == 'change_classroom':
                # 随机选择一个分配进行教室更换
                i = random.randint(0, len(assignments) - 1)
                classroom = random.choice(classrooms)
                
                neighbor = self._change_classroom(assignments, i, classroom['id'])
                if neighbor:
                    fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
                    
                    if fitness > current_fitness:
                        return neighbor, fitness
        
        return assignments, current_fitness
    
    def _random_search(self, assignments: List[Assignment],
                      teachers: List[Dict], classrooms: List[Dict]) -> tuple:
        """随机搜索"""
        # 随机选择一种操作
        operation = random.choice(['swap_times', 'move_time', 'change_classroom'])
        
        if operation == 'swap_times' and len(assignments) >= 2:
            i, j = random.sample(range(len(assignments)), 2)
            neighbor = self._swap_times(assignments, i, j)
        elif operation == 'move_time':
            i = random.randint(0, len(assignments) - 1)
            day = random.randint(1, 5)
            time_slot = random.randint(1, 10)
            neighbor = self._move_time(assignments, i, day, time_slot)
        else:  # change_classroom
            i = random.randint(0, len(assignments) - 1)
            classroom = random.choice(classrooms)
            neighbor = self._change_classroom(assignments, i, classroom['id'])
        
        if neighbor:
            fitness = self.constraint_manager.evaluate_schedule(neighbor)['overall_fitness']
            return neighbor, fitness
        else:
            current_fitness = self.constraint_manager.evaluate_schedule(assignments)['overall_fitness']
            return assignments, current_fitness
    
    def _swap_times(self, assignments: List[Assignment], i: int, j: int) -> List[Assignment]:
        """交换两个分配的时间"""
        neighbor = [a.copy() for a in assignments]
        
        # 交换时间信息
        neighbor[i].day_of_week, neighbor[j].day_of_week = neighbor[j].day_of_week, neighbor[i].day_of_week
        neighbor[i].time_slot, neighbor[j].time_slot = neighbor[j].time_slot, neighbor[i].time_slot
        
        return neighbor
    
    def _move_time(self, assignments: List[Assignment], i: int, 
                  new_day: int, new_time_slot: int) -> Optional[List[Assignment]]:
        """移动一个分配的时间"""
        neighbor = [a.copy() for a in assignments]
        
        # 更新时间
        neighbor[i].day_of_week = new_day
        neighbor[i].time_slot = new_time_slot
        
        return neighbor
    
    def _change_classroom(self, assignments: List[Assignment], i: int, 
                         new_classroom_id: int) -> Optional[List[Assignment]]:
        """更换一个分配的教室"""
        neighbor = [a.copy() for a in assignments]
        
        # 更新教室
        neighbor[i].classroom_id = new_classroom_id
        
        return neighbor
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'iterations': 0,
            'improvements': 0,
            'best_fitness': float('-inf'),
            'initial_fitness': 0.0,
            'final_fitness': 0.0,
        }
